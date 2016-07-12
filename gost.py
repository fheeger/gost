#Copyright (C) 2015 - 2016 Felix Heeger, Lukas Fischer
#
#This file is part of GOST: GeO Survey Tool.
#
#GOST is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#GOST is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with GOST.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import time
import traceback

import bpy
import bmesh
from mathutils import Vector

from PyQt5 import QtSerialPort
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer, Qt, QIODevice

from .tachy import TachyConnection, Timeout
from .util import getSelectedObject, getContext, rad2gon

class MeasureLog(object):
    """Class to manage logging.
    
    This will write all measured points to the automatic log file
    and also store them and print them in a different format later.
    """
    
    knownFormats = ["std", "dat"]
    
    def __init__(self, outPath=None, format="std", append=False):
        self.measurments = []
        if format not in self.knownFormats:
            raise ValueError("%s is not a known format" % format)
        self.format = format
        if append:
            mode = "a"
        else:
            mode = "w"
        if outPath is None:
            outPath = os.path.join(os.path.expanduser("~"),  "%s_gostlog.txt" % time.strftime("%Y-%m-%d_%H-%M-%S"))
        self.out = open(outPath, mode)
        
    def __del__(self):
        """On destruction close the logging stream"""
        self.out.flush()
        self.out.close()
        
    def addPoint(self, pData):
        """Add a point to the log. 
        
        The data will be written imidiatly (in default format) and stored togehter 
        with the time it was added to the log.
        """
        #the measurment is stored together with the time it was created
        self.measurments.append((time.localtime(), pData)) 
        #imediatly write the measurement with standard parameters
        self.out.write(self.formatLine())
        self.out.flush()
        
    def formatLine(self, line=None, lineNr=None, format=None):
        """Format inforamtion about a measurement into a line of text
        
        If no measurement is given, the last stored measurment will be used. 
        The format has to be astring from the knownFormats class attribute.
        If no format is given the standard format of this logging object is used.
        """
        if line is None:
            line = self.measurments[-1]
            lineNr = len(self.measurments)
        elif lineNr is None:
            raise ValueError("If line is given a line number as also to be provided")
        if format is None:
            format = self.format
        if format == "std":
            return time.strftime("%d %b %Y %H:%M:%S") + "\t%(ptid)s\t%(targetEast).3f\t%(targetNorth).3f\t%(targetHeight).3f\n" % line[1]
        elif format == "dat":
            return str(lineNr) + "\t%(ptid)s\tX\t%(targetEast).3f\tY\t%(targetNorth).3f\tZ\t%(targetHeight).3f\n" % line[1]
        else:
            raise ValueError("%s is not a known format" % format)
    
    def writeAll(self, outPath, format=None):
        """Write all stored measurments to a file.
        
        Give the path to which the log should be written in outPath.
        The format has to be astring from the knownFormats class attribute.
        If no format is given the standard format of this logging object is used.
        """
        with open(outPath, "w") as out:
            for l, line in enumerate(self.measurments):
                out.write(self.formatLine(line, l+1, format))
        
    
class QtGostApp(QWidget):
    """Gost main window"""

    def __init__(self, parent=None):
        super(QtGostApp, self).__init__(parent)
        print(os.getcwd())
        print(__file__)
        #create buttons
        self.connectButton = QPushButton("Mit Tachymeter verbinden")
        self.stationButton = QPushButton("Freie Stationierung")
        self.setStationButton = QPushButton("Stationierung auf Punkt")
        self.measurePolyButton = QPushButton("Poly-Linie messen")
        self.settingsButton = QPushButton("Standart Einstellungen")
        self.layoutButton = QPushButton("Neues Ansichtsfenster")
        self.exportMeasurmentsButton = QPushButton("Messungen Exportieren")
        #deactivatee buttons that con not be used before a tachy was connected
        self.stationButton.setEnabled(False)
        self.measurePolyButton.setEnabled(False)
        self.setStationButton.setEnabled(False)
        
        #create the gost logo
        logo = QLabel()
        logo.setGeometry(10,10,280,104)
        logo.setPixmap(QPixmap(os.path.join(os.path.split(__file__)[0], "gostLogo.png")))
        logo.setContentsMargins(0, 0, 0, 0)
        
        #create layout for the window and add buttons to the layout
        buttonLayout = QBoxLayout(QBoxLayout.TopToBottom)
        buttonLayout.addWidget(self.connectButton)
        buttonLayout.addWidget(self.stationButton)
        buttonLayout.addWidget(self.setStationButton)
        buttonLayout.addWidget(self.measurePolyButton)
        buttonLayout.addWidget(self.settingsButton)
        buttonLayout.addWidget(self.layoutButton)
        buttonLayout.addWidget(self.exportMeasurmentsButton)
        
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        mainLayout.addWidget(logo, alignment=Qt.AlignTop)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        
        #connect the button to the according function
        self.connectButton.clicked.connect(self.openConnectWindow)
        self.stationButton.clicked.connect(self.openStationWindow)
        self.settingsButton.clicked.connect(self.openSettingsWindow)
        self.setStationButton.clicked.connect(self.openSetStationWindow)
        self.measurePolyButton.clicked.connect(self.measurePoly)
        self.layoutButton.clicked.connect(self.newLayout)
        self.exportMeasurmentsButton.clicked.connect(self.exportMeasurments)
        
        #create the tachy connection object that handels the connection with the tachymeter
        self.connection = TachyConnection()
        #create logging object to log measurments
        self.log = MeasureLog(format="dat")
        
        self.setWindowTitle("GeO Survey Tool - GOST")
        self.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0], "gost.png")))  
        self.setGeometry(10, 30, 300, 600)
    
    
    
    def newLayout(self):
    
       # 'Drücken Sie B um die darzustellenden Objekte zu selektieren'
       
        xmin = float("inf")
        ymin = float("inf")
        zmin = float("inf")
        
        xmax = 0
        ymax = 0
        zmax = 0
        
        for sel in bpy.data.objects:
            if sel.select:
                x = sel.location[0]
                if x > xmax:
                    xmax=x
                if xmin > x:
                    xmin=x
        
                y = sel.location[1]
                if y > ymax:
                    ymax=y
                if ymin > y:
                    ymin=y
                 
                z = sel.location[2]
                if z > zmax:
                    zmax=z
                if zmin > z:
                    zmin=z
                    
        print(xmin, xmax, ymin, ymax, zmin, zmax)
        
        rangex= xmax - xmin
        
        LayposX = xmin + ((xmax - xmin) /2)
        LayposY = ymin + ((ymax - ymin) /2)
        LayposZ = zmax + 20
        
        bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(LayposX, LayposY, LayposZ))
        name = 'Ansichtsfenster'
        
        for sel in bpy.data.objects:
            if sel.select:
                sel.data.name = name
                sel.name = name
        
        bpy.data.cameras[name].type = 'ORTHO'
        if not hasattr(bpy.types.Scene, "paperformat"):
            bpy.types.Scene.paperformat = 'A4'
            

        if bpy.types.Scene.paperformat == 'A4':
            Paperwidth = 29.7
        elif bpy.types.Scene.paperformat == 'A3':
            Paperwidth = 42
        elif bpy.types.Scene.paperformat == 'A2':
            Paperwidth = 59.4
        elif bpy.types.Scene.paperformat == 'A1':
            Paperwidth = 84.1
        elif bpy.types.Scene.paperformat == 'A0':
            Paperwidth = 118.9
            
        bpy.data.cameras[name].ortho_scale = Paperwidth


    
    def openConnectWindow(self):
        try:
            connectWindow = QtGostConnect(self)
            connectWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                                 "Debug Inforamtionen:\n%s" % traceback.format_exc())

    
    def openStationWindow(self):
        try:
            stationWindow = QtGostStation(self)
            stationWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                                 "Debug Inforamtionen:\n%s" % traceback.format_exc())
        
    def openSetStationWindow(self):
        try:
            setStationWindow = QtSetStation(self)
            setStationWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                                 "Debug Inforamtionen:\n%s" % traceback.format_exc())
 
    def openSettingsWindow(self):
        try:
            settingsWindow = QtGostSettings(self)
            settingsWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                                 "Debug Inforamtionen:\n%s" % traceback.format_exc())
    
    def closeEvent(self, event):
        """Close tachy connection when the gost window ist closed"""
        if self.connection.connected:
            print("closing tachy connection")
            self.connection.close()
        event.accept()
        
    def measurePoly(self):
        if not self.connection.connected:
            QMessageBox.critical(self, "Tachymeter nicht verbunden", 
                                 "Es muss zuerst eine Verbindung zum Tachymeter hergestellt werden.")
            return
        try:
            #create a new window for measuring a poly line
            self.mes = QtWaitForPolyLine(self)
            #make the window modal i.e. the rest of gost will be blocked
            self.mes.setWindowModality(Qt.ApplicationModal)
            #connect the finish signal of the new window to the stop function to deal with clean up
            self.mes.finished.connect(self.stopMeasurePoly)
            self.mes.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                                 "Debug Inforamtionen:\n%s" % traceback.format_exc())
        
    def stopMeasurePoly(self):
        """Clean up after measurement of poly line is done"""
        self.connection.port.timeout=None
        self.mes.deleteLater()
        self.mes = None
        
        
    def exportMeasurments(self):
        """Save all measurments in this session to a file"""
        try:
            exportWindow = QtGostExportWindow(self)
            exportWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                         "Debug Inforamtionen:\n%s" % traceback.format_exc())
    
class QtGostSettings(QDialog):
    """Settings Window"""
    
    def __init__(self, parent=None):
        super(QtGostSettings, self).__init__(parent)
        #create and set layout
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        
        self.defaultButton = QPushButton("Standart wiederherstellen")
        mainLayout.addWidget(self.defaultButton, 4, 0)
        self.defaultButton.clicked.connect(self.standartSettings)


        self.SetDpi = QSpinBox()
        mainLayout.addWidget(QLabel("Dpi:"), 3, 0)
        mainLayout.addWidget(self.SetDpi, 3, 1)
        self.SetDpi.setRange(50, 1000)
        try:
            self.SetDpi.setValue(bpy.types.Scene.paperdpi)
        except AttributeError:
            self.SetDpi.setValue(150)
            bpy.types.Scene.paperdpi = 150
            
            

        self.selectUseKontur = QCheckBox(self)
        mainLayout.addWidget(QLabel("Konturen rendern:"), 0, 0)
        mainLayout.addWidget(self.selectUseKontur, 0, 1)


        self.selectDinFormat = QComboBox(self)
        mainLayout.addWidget(QLabel("DIN Format Rendern:"),1, 0)
        mainLayout.addWidget(self.selectDinFormat, 1, 1)
        self.selectDinFormat.addItems(['A4','A3','A2','A1','A0'])
        self.selectDinFormat.currentIndexChanged.connect(self.computeRes)
        self.SetDpi.valueChanged.connect(self.computeRes)
        try:
            if bpy.types.Scene.paperformat == 'A4':
                self.selectDinFormat.setCurrentIndex(0)
            elif bpy.types.Scene.paperformat == 'A3':
                self.selectDinFormat.setCurrentIndex(1)
            elif bpy.types.Scene.paperformat == 'A2':
                self.selectDinFormat.setCurrentIndex(2)
            elif bpy.types.Scene.paperformat == 'A1':
                self.selectDinFormat.setCurrentIndex(3)
            elif bpy.types.Scene.paperformat == 'A0':
                self.selectDinFormat.setCurrentIndex(4)
        except AttributeError:
            bpy.types.Scene.paperformat = 'A4'
            self.selectDinFormat.setCurrentIndex(0)


        self.selectBackCol = QPushButton("Color")
        mainLayout.addWidget(QLabel("Hintergrundfarbe:"), 2, 0)
        mainLayout.addWidget(self.selectBackCol, 2,1)
        self.selectBackCol.clicked.connect(self.pickColor)

        self.okButton = QPushButton("Ok")
        mainLayout.addWidget(self.okButton, 4, 2)
        self.okButton.clicked.connect(self.accept)
        self.okButton.setDefault(True)

        self.cancleButton = QPushButton("Abbrechen")
        mainLayout.addWidget(self.cancleButton, 4, 1)
        self.cancleButton.clicked.connect(self.reject)


        if bpy.data.scenes[0].render.use_freestyle:
            self.selectUseKontur.setCheckState(2)


    def pickColor(self):
        backCol = QColorDialog(self).getColor()
        red = backCol.red() /255
        green = backCol.green() /255
        blue = backCol.blue() /255
        RgbCol = (red, green, blue)
        bpy.data.scenes[0].world.horizon_color = RgbCol


    def accept(self):
        if self.selectUseKontur.isChecked():
            bpy.data.scenes[0].render.use_freestyle = True
        else:
            bpy.data.scenes[0].render.use_freestyle = False
        super(QtGostSettings, self).accept()


    def standartSettings(self):
        bpy.data.scenes[0].render.use_freestyle = True
        self.selectUseKontur.setCheckState(2)
        
        bpy.types.Scene.paperformat = 'A4'
        self.selectDinFormat.setCurrentIndex(0)

        bpy.data.scenes[0].world.horizon_color = (1,1,1)

        self.SetDpi.setValue(150)

    def computeRes(self):
        dpi = self.SetDpi.value()

        bpy.types.Scene.paperdpi=dpi

        paperformat = self.selectDinFormat.currentText()
        bpy.types.Scene.paperformat=paperformat

        
        if paperformat == 'A4':
            bpy.data.scenes[0].render.resolution_x = (29.7 / 2.5)*dpi
            bpy.data.scenes[0].render.resolution_y = (21 / 2.5)*dpi
            
        elif paperformat == 'A3':
            bpy.data.scenes[0].render.resolution_x = (42 / 2.5)*dpi
            bpy.data.scenes[0].render.resolution_y = (29.7 / 2.5)*dpi
            
        elif paperformat == 'A2':
            bpy.data.scenes[0].render.resolution_x = (59.4 / 2.5)*dpi
            bpy.data.scenes[0].render.resolution_y = (42 / 2.5)*dpi
            
        elif paperformat == 'A1':
            bpy.data.scenes[0].render.resolution_x = (84.1 / 2.5)*dpi
            bpy.data.scenes[0].render.resolution_y = (59.4 / 2.5)*dpi
            
        elif paperformat == 'A0':
            bpy.data.scenes[0].render.resolution_x = (118.9 / 2.5)*dpi
            bpy.data.scenes[0].render.resolution_y = (84.1 / 2.5)*dpi




class QtGostConnect(QDialog):
    """Window for Connecting to the Tachymeter via COM port."""
    posBautRates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    
    def __init__(self, parent=None):
        super(QtGostConnect, self).__init__(parent)
        
        self.selectPort = QComboBox(self)
        for port in self.avail_ports():
            self.selectPort.addItem(port)
        self.selectBautRate = QComboBox(self)
        self.selectBautRate.addItems([str(b) for b in self.posBautRates])
        self.selectBautRate.setCurrentIndex(11)
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        
                
        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel("COM port:"), 0, 0)
        mainLayout.addWidget(self.selectPort, 0, 1)
        mainLayout.addWidget(QLabel("Baut rate:"),1, 0)
        mainLayout.addWidget(self.selectBautRate, 1, 1)
        mainLayout.addWidget(self.okButton, 2, 0)
        mainLayout.addWidget(self.cancleButton, 2, 1)
        self.setLayout(mainLayout)
 
        self.okButton.clicked.connect(self.accept) 
        self.cancleButton.clicked.connect(self.reject)

    def avail_ports(self):
        """Get a list of available COM ports."""
        return sorted([p.portName() for p in QtSerialPort.QSerialPortInfo.availablePorts() if not p.isBusy()])

    def accept(self):
        """On Accept signal connect to the chosen COM port."""
        #get the chosen options from the window
        port = self.selectPort.currentText()
        bautrate = int(self.selectBautRate.currentText())
        print("connecting to port: %s, with baut rate %i" % (port, bautrate))
        #connect to the port
        self.parentWidget().connection.open(port, bautrate)
        #enable buttons in the main window that only work with Tachy connected
        self.parentWidget().connectButton.setEnabled(False)
        self.parentWidget().stationButton.setEnabled(True)
        self.parentWidget().measurePolyButton.setEnabled(True)
        self.parentWidget().setStationButton.setEnabled(True)
   
        # self.meassureButton.setEnabled(True)
        super(QtGostConnect, self).accept()
    
class QtGostStation(QDialog):
    
    """Window for Free Stationing"""
    def __init__(self, parent=None):
        super(QtGostStation, self).__init__(parent)
        
        self.pointList = QTableWidget(self)
        self.pointList.setColumnCount(7)
        self.pointList.setHorizontalHeaderLabels(["Name","X","Y","Z","Abweichung","",""])
        self.xLab = QLabel("NA")
        self.yLab = QLabel("NA")
        self.zLab = QLabel("NA")
        self.errorLab = QLabel("NA")
        self.computeButton = QPushButton("Station Berechnen")
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        self.addPointButton = QPushButton("Punkt Hinzufügen")
        
        mainLayout = QBoxLayout(2)
        mainLayout.addWidget(QLabel("Derzeitige Stationierung:"))
        
        stationLayout = QBoxLayout(0)
        stationLayout.addWidget(QLabel("x:"))
        stationLayout.addWidget(self.xLab)
        stationLayout.addWidget(QLabel("y:"))
        stationLayout.addWidget(self.yLab)
        stationLayout.addWidget(QLabel("z:"))
        stationLayout.addWidget(self.zLab)
        stationLayout.addWidget(QLabel("std. Fehler:"))
        stationLayout.addWidget(self.errorLab)
        
        mainLayout.addLayout(stationLayout)
        mainLayout.addWidget(self.pointList)
        mainLayout.addWidget(self.addPointButton)
        
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.okButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.cancleButton, QDialogButtonBox.RejectRole)
        buttonBox.addButton(self.computeButton, QDialogButtonBox.ApplyRole)
        
        mainLayout.addWidget(buttonBox)
        
        self.setLayout(mainLayout)

        self.okButton.clicked.connect(self.accept)
        self.okButton.setEnabled(False)
        self.cancleButton.clicked.connect(self.reject)
        self.addPointButton.clicked.connect(self.startAddPoint)
        self.computeButton.clicked.connect(self.computeStation)

        #this list will hold the measurments for each point
        self.pointData = []
        self.setGeometry(10, 30, 800, 600)

    def startAddPoint(self):
        """Start adding a point.
        
        This means open the smal inforamtion window and wait for user input 
        while the rest of the gost windows are deactivated."""
        #deselecht all objects, because we want to choose a new one.
        for obj in bpy.data.objects:
            obj.select = False
        self.wait = QtWaitForSelection(self)
        self.wait.setWindowModality(Qt.ApplicationModal)
        self.wait.show()
        self.hide()
        #connect the closing of the window to processing the results
        self.wait.finished.connect(self.addPoint)

    def addPoint(self, result):
        """Process result from point selection."""
        #if the result was "accept" process it
        if result == QDialog.Accepted:
            name = self.wait.selected.name
            #was this point already added?
            for i in range(self.pointList.rowCount()):
                if self.pointList.item(i, 0).text() == name:
                    QMessageBox.critical(self, "Punkt Bereits Vorhanden", "Dieser Punkt wurde bereits hinzugefügt.")
                    self.wait.deleteLater()
                    self.wait = None
                    self.show()
                    return
            #add a row to the point table
            self.pointList.setRowCount(self.pointList.rowCount() + 1)
            #get point coordinates from the selection message window
            x,y,z = self.wait.selected.location
            #add content to the new point table row
            self.pointList.setItem(self.pointList.rowCount()-1, 0, QTableWidgetItem(name))
            self.pointList.setItem(self.pointList.rowCount()-1, 1, QTableWidgetItem(str(x)))
            self.pointList.setItem(self.pointList.rowCount()-1, 2, QTableWidgetItem(str(y)))
            self.pointList.setItem(self.pointList.rowCount()-1, 3, QTableWidgetItem(str(z)))
            remButton = QPushButton("Punkt löschen")
            remButton.clicked.connect(self.removePoint)
            self.pointList.setCellWidget(self.pointList.rowCount()-1, 5, remButton)
            measButton = QPushButton("Punkt messen")
            measButton.clicked.connect(self.startMeasurePoint)
            self.pointList.setCellWidget(self.pointList.rowCount()-1, 6, measButton)
            #create a new entry in the pointData list. this is None until it is measured
            self.pointData.append(None)
        #remove the wait window and show the table window again
        self.wait.deleteLater()
        self.wait = None
        self.show()

    def removePoint(self):
        """Remove a point from the List"""
        #find the row that contains the button that was clicked
        for i in range(self.pointList.rowCount()):
            if self.pointList.cellWidget(i, 5) == self.sender():
                #remove the row
                self.pointList.removeRow(i)
                #remove the entry for this point in the pointData list (measurments)
                self.pointData = self.pointData[:i] + self.pointData[i+1:]
                break
                
    def startMeasurePoint(self):
        """Start measuring a point in the real world."""
        #find the row that contains the button that was clicked
        for index in range(self.pointList.rowCount()):
            if self.pointList.cellWidget(index, 6) == self.sender():
                break
        #open the meassage windiw for measuring a point.
        #Give it the row number (index) so we can retrieve it later
        self.measure = QtWaitForMeasurement(index, self)
        self.measure.setWindowModality(Qt.ApplicationModal)
        self.measure.show()
        self.hide()
        #connect the closing of the window to processing the results
        self.measure.finished.connect(self.measurePoint)
        
    def measurePoint(self):
        """Process results from measuring a point"""
        #save the measured data into the list at the position that was given when 
        # opening the window
        if hasattr(self.measure, "data"):
            #if the measurement was canceled this does not happen
            self.pointData[self.measure.index] = self.measure.data
        #mark the row green
        self.pointList.item(self.measure.index, 0).setBackground(QColor(0,200,0))
        #close the meassage window and show the table window

        self.measure.deleteLater()
        self.measure = None
        self.show()
    
    def computeStation(self):
        """Compute the station from all measured data """
        print(len(self.pointData))
        #check if there are enough points measured, we need at least 3
        if sum([not x is None for x in self.pointData]) < 3:
            QMessageBox.critical(self, "Nicht Genug Punkte", "Es sind nicht genug Punkte für die Stationierung eingemessen.")
            return
        
        gostApp = self.parentWidget()
        #get the position of the first fix point
        p1 = (float(self.pointList.item(0,1).text()),
              float(self.pointList.item(0,2).text()),
              float(self.pointList.item(0,3).text()))
        #run the addition of the first fix point in the Tachy object
        gostApp.connection.stationPoint1(p1, self.pointData[0])
        #for each additional point (at least 2), get the position from the table and
        # run the function for adding a point in the Tachy object
        for i in range(1, self.pointList.rowCount()):
            p = (float(self.pointList.item(i,1).text()),
                 float(self.pointList.item(i,2).text()),
                 float(self.pointList.item(i,3).text()))
            gostApp.connection.stationPointN(p, self.pointData[i])
        #run the compute station funnction in the Tachy object
        # get the computed station position, correction angle and the estimated error
        pos, angle, error = gostApp.connection.computeStation()
        #display the information in the table window
        self.xLab.setText(str(pos[0]))
        self.yLab.setText(str(pos[1]))
        self.zLab.setText(str(pos[2]))
        self.errorLab.setText(str(error))
        self.rotAngle = angle
        self.okButton.setEnabled(True)
        
    def accept(self):
        """Accept computed station"""
        gostApp = self.parentWidget()
        #get the station position and rotation angle that was computed
        pos = (float(self.xLab.text()), float(self.yLab.text()), float(self.zLab.text()))
        a = self.rotAngle
        #get the current horizontal angle of the tachy
        currentAngle = gostApp.connection.getAngle()
        print("current angle: %f gon" % currentAngle)
        print("rotation angle: %f gon" % rad2gon(a))
        #use the rotation angle and the current (wrong) angle to compute the real angle of the tachy
        angle = (currentAngle + rad2gon(a)) % 400
        #run the the set station funtion of the Tachy object which whil transfer the data to the Tachymeter
        gostApp.connection.setStation(pos, angle)
        super(QtGostStation, self).accept()
        
class QtWaitForPolyLine(QDialog):
    """Window for polyline measurments."""
    
    def __init__(self, parent=None):
        super(QtWaitForPolyLine, self).__init__(parent=parent)
        
        self.setWindowTitle("Warte auf Messungen")
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(QLabel("Bitte Punkte mit dem Tachymeter messen!"))
        
        self.closeButton = QPushButton("Linie schließen")
        self.closeButton.clicked.connect(self.closeLine)
        self.breakButton = QPushButton("Linie unterbrechen")
        self.breakButton.clicked.connect(self.breakLine)
        self.endButton = QPushButton("Messung beenden")
        self.endButton.clicked.connect(self.reject)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.breakButton)
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.endButton)
        
        mainLayout.addLayout(buttonLayout)
        
        self.setLayout(mainLayout)
        
        #short cut keys
        closeKeyC = QShortcut(QKeySequence("C"), self)
        closeKeyC.activated.connect(self.closeLine)
        closeKeyS = QShortcut(QKeySequence("S"), self)
        closeKeyS.activated.connect(self.closeLine)
        breakKeyB = QShortcut(QKeySequence("B"), self)
        breakKeyB.activated.connect(self.breakLine)
        breakKeyU = QShortcut(QKeySequence("U"), self)
        breakKeyU.activated.connect(self.breakLine)
        
        self.move(0,0)

        #connect recieving something on the COM port to the function processing it
        self.parentWidget().connection.port.readyRead.connect(self.recieveMeasurment)
        
        #deselect all objects
        for obj in bpy.data.objects:
            obj.select = False
        
    def recieveMeasurment(self):
        #set timeout to None
        oldTimeout = self.parentWidget().connection.timeout
        self.parentWidget().connection.timeout = None
        #get measurment from the Tachy object
        measurement = self.parentWidget().connection.readMeasurement()
        #reset timeout
        self.parentWidget().connection.timeout = oldTimeout
        #if no data was returned (because no full measurment 
        # has arrived at the COM port yet) stop execution
        if measurement is None:
            return
        print("measure")
        #get coordinates from the measurment data
        x = measurement["targetEast"]
        y = measurement["targetNorth"]
        z = measurement["targetHeight"] 
        try:
            obj = getSelectedObject()
        except ValueError:
            QMessageBox.critical(self, "Mehrer Objekt Ausgewählt", 
                                 "Es darf nicht mehr als ein Objekt ausgewählt sein.")
        else:
            if obj is None:
                #if no object is selected, create a new one at the measured location
                print("No object selected")
                #create a new mesh with one point with local (inside the mesh) coordinates 0,0,0
                mesh = bpy.data.meshes.new(name="New Mesh")
                mesh.from_pydata([Vector((0,0,0))], [], [])
                #create an object with the mesh
                obj = bpy.data.objects.new("New Object", mesh)
                #put the object at the measured coordinates
                obj.location = (x,y,z)
                #link the object into the scene
                bpy.data.scenes[0].objects.link(obj)
                obj.select=True
            else:  
                #if an object is selected, add it a new point to it at the measured location
                #add a vertex
                obj.data.vertices.add(1)
                #get the global coordinates of the object
                ol = obj.location
                #set the new vertex local (inside the object) coordinates so that it is at
                # the measured coordinates in the global context
                #this is done by getting the difference between measured (global) coordinates and
                # the location of the object (which is the reference point for the local coordinate system)
                obj.data.vertices[-1].co = (x-ol[0], y-ol[1], z-ol[2])
                #add an edge and set its start and end point to the last and secon to last vertex
                obj.data.edges.add(1)
                obj.data.edges[-1].vertices = [len(obj.data.vertices)-1, len(obj.data.vertices)-2]
            #update the scene so changes in the mesh a displayed correctly
            bpy.data.scenes[0].update()
            
    def closeLine(self):
        """Close the poly line.
        
        This includes:
        1) creating an edge between the last and the first vertex
        2) mark the outer edges as "freestyle" edges to plot them as lines later
        3) fill the mesh i.e. create face inside it
        4) recomupte the normales of the faces
        5) make the shading of the faces smooth so it does not show shadows in the plot"""
        
        print("closing line")
        #check conditions for closing a line
        try:
            #not more than one selected object
            obj = getSelectedObject()
        except ValueError:
            QMessageBox.critical(self, "Mehrer Objekt Ausgewählt", 
                                 "Es darf nicht mehr als ein Objekt ausgewählt sein.")
            return
        if obj is None:
            #at least one selected object
            QMessageBox.critical(self, "Kein Objekt Ausgewählt", 
                                       "Es muss eine Linie ausgewählt sein um sie zu schließen.")
            return
        if len(obj.data.vertices) < 3:
            #at least 3 vertices in the selected object
            QMessageBox.critical(self, "Zu Wenig Punkte", 
                                       "Das ausgewählte Objekt enthält zu wenig Punkte zum schließen.")
            return
        #add the final edge between last and first vertex
        obj.data.edges.add(1)
        obj.data.edges[-1].vertices = [len(obj.data.vertices)-1, 0]
        bpy.data.scenes[0].update()
        bpy.data.scenes[0].objects.active = obj
        #prepare a fake context for the bpy.ops fuctions to work with
        context = getContext()
        context["active_object"] = obj
        print(context)
        #go to edit mode
        bpy.ops.object.mode_set(context, mode='EDIT')
        b = bmesh.from_edit_mesh(obj.data)
        #mark edeges for freestyle render (select all edges first)
        for e in b.edges:
            e.select=True
        bpy.ops.mesh.mark_freestyle_edge(context, clear=False)
        #fill
        bpy.ops.mesh.fill(context)
        #recalculate normals
        bpy.ops.mesh.normals_make_consistent(context)
        bpy.ops.object.mode_set(context, mode='OBJECT')
        #make shading smooth
        bpy.ops.object.shade_smooth()
        #deselect the object so the next measurment starts a new mesh
        obj.select = False
        
    def breakLine(self):
        """Break the poly line."""
        print("breaking line")
        #check for prequesites to breking the line
        try:
            #not more than one object selected
            obj = getSelectedObject()
        except ValueError:
            QMessageBox.critical(self, "Mehrer Objekt Ausgewählt", 
                                 "Es darf nicht mehr als ein Objekt ausgewählt sein.")
            return
        if obj is None:
            #at least one object selected
            QMessageBox.critical(self, "Kein Objekt Ausgewählt", 
                                 "Es muss eine Linie ausgewählt sein um sie zu unterbrechen.")
            return
        #deselect the object so the next measurment starts a new mesh i.e. the line is broken
        obj.select = False
                

        
class QtWaitForSelection(QMessageBox):
    """Window to wait for the user to select an object"""
    def __init__(self, parent=None):
        super(QtWaitForSelection, self).__init__(QMessageBox.Question, "Warte auf Auswahl",
                                                 "Bitte wählen sie ein Object im 3d view  aus",
                                                 buttons=QMessageBox.Cancel,
                                                 parent=parent)
        self.move(0,0)
        #create a timer
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        #connect the timer to checking is anything was selected
        self.timer.timeout.connect(self.pollSelection)
        self.timer.start()
        self.selected = None

    def pollSelection(self):
        """Check if anything was selected"""
        try:
            #get the selected object
            nowSelected = getSelectedObject()
        except ValueError:
            QMessageBox.critical(self, "Mehrer Objekt Ausgewählt", 
                                 "Es darf nicht mehr als ein Objekt ausgewählt sein.")
            for obj in bpy.data.objects:
                obj.select = False
        else:
            if not nowSelected is None:
                #stotre the selected object
                self.selected = nowSelected
                #stop the timer and close the window
                self.timer.stop()
                self.accept()

class QtWaitForMeasurement(QMessageBox):
    """Window to wait for a single Measurment"""
    
    def __init__(self, index, parent=None):
        super(QtWaitForMeasurement, self).__init__(QMessageBox.Question, "Warte auf Messung",
                                                   "Bitte führen sie eine Messung mit dem Tachymeter durch",
                                                   buttons=QMessageBox.Cancel,
                                                   parent=parent)
        self.move(0,0)
        self.index = index
        #connect the arrival of data at the COM port to a function to process it
        self.parentWidget().parentWidget().connection.port.readyRead.connect(self.recieveMeasurment)

    def recieveMeasurment(self):
        """Process measurment."""
        
        #try to get a full measurment
        self.data = self.parentWidget().parentWidget().connection.readMeasurement()
        if not self.data is None:
            #if a full measurment was rcieved
            #save measured data to the log
            self.parentWidget().parentWidget().log.addPoint(self.data)
            #cloose the window
            self.accept()
 
class QtSetStation(QDialog):
    """Window for setting the station manually"""
    
    def __init__(self, parent=None):
        super(QtSetStation, self).__init__(parent)
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        self.xField = QLineEdit()
          
        self.yField = QLineEdit()
        self.zField = QLineEdit()
        self.angleField = QLineEdit()
        
        xpos,ypos,zpos=self.parentWidget().connection.getPosition() # getPosition fonction for tachy does not work
   
        self.xField.setText(str(xpos))   
        self.yField.setText(str(ypos))
        self.zField.setText(str(zpos))
        self.angleField.setText(str(self.parentWidget().connection.getAngle()))        
        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel("X:"), 0, 0)
        mainLayout.addWidget(self.xField, 0, 1)
        mainLayout.addWidget(QLabel("Y:"),1, 0)
        mainLayout.addWidget(self.yField, 1, 1)
        mainLayout.addWidget(QLabel("Z:"),2, 0)
        mainLayout.addWidget(self.zField, 2, 1)
        mainLayout.addWidget(QLabel("Winkel:"),3, 0)
        mainLayout.addWidget(self.angleField, 3, 1)
        mainLayout.addWidget(self.okButton, 4, 0)
        mainLayout.addWidget(self.cancleButton, 4, 1)
        self.setLayout(mainLayout)
        
        self.okButton.clicked.connect(self.accept) 
        self.cancleButton.clicked.connect(self.reject)
        
    def accept(self):
        #get the input data from the form
        p = (float(self.xField.text()),
             float(self.yField.text()),
             float(self.zField.text()))
        a = float(self.angleField.text())
        #run the function to set the station from the Tachy object
        self.parentWidget().connection.setStation(p, a)
        super(QtSetStation, self).accept()

class QtGostExportWindow(QDialog):
    """Window for saving all measured points to a file"""
    def __init__(self, parent=None):
        super(QtGostExportWindow, self).__init__(parent)
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)
        
        #create a drop down menu with all formats that are know to the loggin object
        self.selectFormat = QComboBox(self)
        for format in self.parentWidget().log.knownFormats:
            self.selectFormat.addItem(format)
        
        self.saveButton = QPushButton("Speichern")
        
        mainLayout.addWidget(QLabel("Format auswählen:"), 0, 0)
        mainLayout.addWidget(self.selectFormat, 0, 1)
        mainLayout.addWidget(self.saveButton, 1,1)
        self.saveButton.clicked.connect(self.save)

    def save(self):
        """Save the data"""
        #get the file name from the user with a file dialog
        fileName = QFileDialog.getSaveFileName(self, "Messungen exporiteren", os.path.expanduser("~"))[0]
        print(fileName)
        if len(fileName) == 0:
            self.reject()
        else:
            self.parentWidget().log.writeAll(fileName, self.selectFormat.currentText())
            self.accept()
        
# class QtNivel(QDialog):
    # def __init__(self, parent=None):
        # super(QtNivel, self).__init__(parent)
        

        
        # self.xField = QLineEdit()
        # self.yField = QLineEdit()
        # self.zField = QLineEdit()
        
        # mainLayout = QGridLayout()
        # mainLayout.addWidget(QLabel("x:"), 0, 0)
        # mainLayout.addWidget(self.xField , 0, 1)
        # mainLayout.addWidget(QLabel("y:"), 1, 0)
        # mainLayout.addWidget(self.yField, 1, 1)
        # mainLayout.addWidget(QLabel("z:"), 2, 0)
        # mainLayout.addWidget(self.zField, 2, 1)
        
        # button = QPushButton('Add Nivelement', self)
        # mainLayout.addWidget(button, 3, 0)
        
        # self.setLayout(mainLayout)
        
        # button.clicked.connect(self.addNivel)
        
    # def addNivel(self, *args):
          
        # global context
            
        # x = float(self.xField.text()) 
        # y = float(self.yField.text())
        # z = float(self.zField.text())
        
        # print("creating niv at %f,%f,%f" % (x,y,z))
        
        # #context["scene"].cursor_location = (x, y, z)
        # bpy.context.scene.cursor_location = (x, y, z)
        
        # strval = "%.2f m NN" % z
        # bpy.ops.object.text_add()
        # ob = bpy.data.objects["Text"]
        # print(str(ob))
        # ob.name = (strval)
        # tcu = ob.data
        # tcu.name = (strval)
        # tcu.body = (strval)
        # tcu.font = bpy.data.fonts[0]
        # tcu.offset_x = -0.01
        # tcu.offset_y = 0.03
        # tcu.shear = 0
        # tcu.size = .06
        # tcu.space_character = 1.1
        # tcu.space_word = 2
        # tcu.extrude = 0.002
        # tcu.fill_mode="FRONT"
        # tcu.use_fill_deform = True
        # tcu.fill_mode="FRONT"

       
        # coords = [[0, 0, 0], [-0.016, 0.024, 0], [0.016, 0.024, 0]]
        # faces = [[0,2,1]]
        
        # me = bpy.data.meshes.new("Triangle")
        # tr = bpy.data.objects.new("Triangle", me)
        # #bpy.context.scene.objects.link(ob)
        # tr.location = context["scene"].cursor_location
        # context["scene"].objects.link(tr)
        # #mesh.from_pydata([context.scene.cursor_location], [], [])
        # me.from_pydata(coords, [], faces)
        # me.update()
        # context["scene"].objects.active = ob
