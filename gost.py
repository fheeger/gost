#Copyright (C) 2015 - 2016 Felix Heeger
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

import bpy
import bmesh
from mathutils import Vector

import serial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer, Qt

from .tachy import TachyConnection, Timeout
from .util import getSelectedObject, getContext, rad2gon

class MeasureLog(object):
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
        self.out.flush()
        self.out.close()
        
    def addPoint(self, pData):
        self.measurments.append((time.localtime(), pData))
        self.out.write(self.formatLine())
        self.out.flush()
        
    def formatLine(self, line=None, lineNr=None, format=None):
        if line is None:
            line = self.measurments[-1]
            lineNr = len(self.measurments)
        if format is None:
            format = self.format
        if format == "std":
            return time.strftime("%d %b %Y %H:%M:%S") + "\t%(ptid)s\t%(targetEast).3f\t%(targetNorth).3f\t%(targetHeight).3f\n" % line[1]
        elif format == "dat":
            return str(lineNr) + "\t%(ptid)s\tX\t%(targetEast).3f\tY\t%(targetNorth).3f\tZ\t%(targetHeight).3f\n" % line[1]
        else:
            raise ValueError("%s is not a known format" % format)
    
    def writeAll(self, outPath, format=None):
        with open(outPath, "w") as out:
            for l, line in enumerate(self.measurments):
                out.write(self.formatLine(line, l+1, format))
        
    
class QtGostApp(QWidget):
    def __init__(self, parent=None):
        super(QtGostApp, self).__init__(parent)
        print(os.getcwd())
        print(__file__)
        self.connectButton = QPushButton("Mit Tachymeter verbinden")
        self.stationButton = QPushButton("Freie Stationierung")
        self.setStationButton = QPushButton("Stationierung auf Punkt")
        self.measurePolyButton = QPushButton("Poly-Linie messen")
        self.settingsButton = QPushButton("Standart Einstellungen")
        self.layoutButton = QPushButton("Neues Ansichtsfenster")
        self.exportMeasurmentsButton = QPushButton("Messungen Exportieren")
        self.stationButton.setEnabled(False)
        
        logo = QLabel()
        logo.setGeometry(10,10,280,104)
        logo.setPixmap(QPixmap(os.path.join(os.path.split(__file__)[0], "gostLogo.png")))
        logo.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.connectButton.clicked.connect(self.openConnectWindow)
        self.stationButton.clicked.connect(self.openStationWindow)
        self.settingsButton.clicked.connect(self.openSettingsWindow)
        self.setStationButton.clicked.connect(self.openSetStationWindow)
        self.measurePolyButton.clicked.connect(self.measurePoly)
        self.layoutButton.clicked.connect(self.newLayout)
        self.exportMeasurmentsButton.clicked.connect(self.exportMeasurments)
        
        self.connection = TachyConnection()
        self.log = MeasureLog(format="dat")
        
        self.setWindowTitle("GeO Survey Tool - GOST")
        self.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0], "gost.png")))  
        self.setGeometry(10, 30, 300, 600)
    
    
    #kleinsten und größten Wert herausfinden!
    
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
        except:
            error=QErrorMessage(self)
            error.showMessage('Can not connect to Tachy')

    
    def openStationWindow(self):
        stationWindow = QtGostStation(self)
        stationWindow.show()
        
    def openSetStationWindow(self):
        setStationWindow = QtSetStation(self)
        setStationWindow.show()
        
    def openSettingsWindow(self):
        settingsWindow = QtGostSettings(self)
        settingsWindow.show()
    
    def closeEvent(self, event):
        if self.connection.connected:
            print("closing tachy connection")
            self.connection.close()
        event.accept()
        
    def measurePoly(self):
        self.mes = QtWaitForPolyLine(self)
        self.mes.setWindowModality(Qt.ApplicationModal)
        self.mes.finished.connect(self.stopMeasurePoly)
        self.mes.show()
        
    def stopMeasurePoly(self):
        self.mes.timer.stop()
        self.connection.port.timeout=None
        self.mes.deleteLater()
        self.mes = None
        
        
    def exportMeasurments(self):
        exportWindow = QtGostExportWindow(self)
        exportWindow.show()
    
class QtGostSettings(QDialog):
    
    def __init__(self, parent=None):
        super(QtGostSettings, self).__init__(parent)
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        self.defaultButton = QPushButton("Standart wiederherstellen")
        mainLayout.addWidget(self.defaultButton, 4, 0)
        self.defaultButton.clicked.connect(self.standartSettings)


        self.SetDpi = QSpinBox()
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

        self.SetDpi.setDisplayIntegerBase(150)


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
        if sys.platform[:3] == "win":
            possible = ["COM%i" % i for i in range(1,255)]
        else:
            possible = glob("/dev/tty[a-zA-Z]*")
        ports = []
        for p in possible:
            try:
                serial.Serial(p).close()
            except serial.SerialException:
                pass
            else:
                ports.append(p)
        # uncommend this line with the according path for pseudo ports in linux
        #ports.append("/dev/pts/18")
        return ports

    def accept(self):
        port = self.selectPort.currentText()
        bautrate = int(self.selectBautRate.currentText())
        print("connecting to port: %s, with baut rate %i" % (port, bautrate))
        self.parentWidget().connection.open(port, bautrate)
        self.parentWidget().connectButton.setEnabled(False)
        self.parentWidget().stationButton.setEnabled(True)
        # self.meassureButton.setEnabled(True)
        super(QtGostConnect, self).accept()
    
class QtGostStation(QDialog):
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

        self.pointData = []
        self.setGeometry(10, 30, 800, 600)

    def startAddPoint(self):
        for obj in bpy.data.objects:
            obj.select = False
        nowSelected =  getSelectedObject()
        self.wait = QtWaitForSelection(nowSelected, self)
        self.wait.setWindowModality(Qt.ApplicationModal)
        self.wait.show()
        self.hide()
        self.wait.finished.connect(self.addPoint)

    def addPoint(self, result):
        if result == QDialog.Accepted:
            name = getSelectedObject().name
            #was this point already added?
            for i in range(self.pointList.rowCount()):
                if self.pointList.item(i, 0).text() == name:
                    QMessageBox.critical(self, "Punkt Bereits Vorhanden", "Dieser Punkt wurde bereits hinzugefügt.")
                    self.wait.deleteLater()
                    self.wait = None
                    self.show()
                    return
            self.pointList.setRowCount(self.pointList.rowCount() + 1)
            x,y,z = getSelectedObject().location
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
            self.pointData.append(None)
        self.wait.deleteLater()
        self.wait = None
        self.show()

    def removePoint(self):
        for i in range(self.pointList.rowCount()):
            if self.pointList.cellWidget(i, 5) == self.sender():
                self.pointList.removeRow(i)
                self.pointData = self.pointData[:i] + self.pointData[i+1:]
                break
                
    def startMeasurePoint(self):
        for index in range(self.pointList.rowCount()):
            if self.pointList.cellWidget(index, 6) == self.sender():
                break
        self.measure = QtWaitForMeasurement(index, self)
        self.measure.setWindowModality(Qt.ApplicationModal)
        self.measure.show()
        self.hide()
        self.measure.finished.connect(self.measurePoint)
        
    def measurePoint(self):
        self.pointData[self.measure.index] = self.measure.data
        self.pointList.item(self.measure.index, 0).setBackground(QColor(0,200,0))
        self.measure.deleteLater()
        self.measure = None
        self.show()
    
    def computeStation(self):
        print(len(self.pointData))
        if sum([not x is None for x in self.pointData]) < 3:
            QMessageBox.critical(self, "Nicht Genug Punkte", "Es sind nicht genug Punkte für die Stationierung eingemessen.")
            return
        
        gostApp = self.parentWidget()
        p1 = (float(self.pointList.item(0,1).text()),
              float(self.pointList.item(0,2).text()),
              float(self.pointList.item(0,3).text()))
        gostApp.connection.stationPoint1(p1, self.pointData[0])
        for i in range(1, self.pointList.rowCount()):
            p = (float(self.pointList.item(i,1).text()),
                 float(self.pointList.item(i,2).text()),
                 float(self.pointList.item(i,3).text()))
            gostApp.connection.stationPointN(p, self.pointData[i])
        pos, angle, error = gostApp.connection.computeStation()
        self.xLab.setText(str(pos[0]))
        self.yLab.setText(str(pos[1]))
        self.zLab.setText(str(pos[2]))
        self.errorLab.setText(str(error))
        self.rotAngle = angle
        self.okButton.setEnabled(True)
        
    def accept(self):
        gostApp = self.parentWidget()
        pos = (float(self.xLab.text()), float(self.yLab.text()), float(self.zLab.text()))
        a = self.rotAngle
        currentAngle = gostApp.connection.getAngle()
        print("current angle: %f gon" % currentAngle)
        print("rotation angle: %f gon" % rad2gon(a))
        angle = (currentAngle + rad2gon(a)) % 400
        gostApp.connection.setStation(pos, angle)
        super(QtGostStation, self).accept()
        
class QtWaitForPolyLine(QDialog):
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
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.parentWidget().connection.port.timeout=0.1
        self.timer.timeout.connect(self.pollMeasurement)
        self.timer.start()
        
    def pollMeasurement(self):
        try:
            measurement = self.parentWidget().connection.readMeasurement()
            self.parentWidget().log.addPoint(measurement)
        except Timeout:
            pass
        else:
            print("measure")
            x = measurement["targetEast"]
            y = measurement["targetNorth"]
            z = measurement["targetHeight"] 
            #bpy.context.area.type='VIEW_3D'
            if getSelectedObject() is None:
                print("No object selected")
                mesh = bpy.data.meshes.new(name="New Mesh")
                mesh.from_pydata([Vector((0,0,0))], [], [])
                obj = bpy.data.objects.new("New Object", mesh)
                obj.location = (x,y,z)
                bpy.data.scenes[0].objects.link(obj)
                obj.select=True
            else:  
                obj = getSelectedObject()
                obj.data.vertices.add(1)
                ol = obj.location
                obj.data.vertices[-1].co = (x-ol[0], y-ol[1], z-ol[2])
                obj.data.edges.add(1)
                obj.data.edges[-1].vertices = [len(obj.data.vertices)-1, len(obj.data.vertices)-2]
            bpy.data.scenes[0].update()
            
    def closeLine(self):
        print("closing line")
        obj = getSelectedObject()
        if obj is None:
            QMessageBox.critical(self, "Kein Objekt Ausgewählt", 
                                       "Es muss eine Linie ausgewählt sein um sie zu schließen.")
            return
        if len(obj.data.vertices) < 3:
            QMessageBox.critical(self, "Zu Wenig Punkte", 
                                       "Das ausgewählte Objekt enthält zu wenig Punkte zum schließen.")
            return
        obj.data.edges.add(1)
        obj.data.edges[-1].vertices = [len(obj.data.vertices)-1, 0]
        bpy.data.scenes[0].update()
        bpy.data.scenes[0].objects.active = obj
        context = getContext()
        context["active_object"] = obj
        # context["object"] = obj
        # context["active_object"] = obj
        # context["scene"] = bpy.data.scenes[0]
        # context["edit_object"] = None
        print(context)
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
        print("breaking line")
        obj = getSelectedObject()
        if obj is None:
            QMessageBox.critical(self, "Kein Objekt Ausgewählt", 
                                 "Es muss eine Linie ausgewählt sein um sie zu unterbrechen.")
            return
        #deselect the object so the next measurment starts a new mesh
        obj.select = False
                

        
class QtWaitForSelection(QMessageBox):
    def __init__(self, nowSelected, parent=None):
        super(QtWaitForSelection, self).__init__(QMessageBox.Question, "Warte auf Auswahl",
                                                 "Bitte wählen sie ein Object im 3d view  aus",
                                                 buttons=QMessageBox.Cancel,
                                                 parent=parent)
        self.move(0,0)
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.pollSelection)
        self.timer.start()
        self.oldSelected = nowSelected
        self.newSelected = None

    def pollSelection(self):
        nowSelected = getSelectedObject()
        if not nowSelected == self. oldSelected:
            self.newSelected = nowSelected
            self.timer.stop()
            self.accept()

class QtWaitForMeasurement(QMessageBox):
    def __init__(self, index, parent=None):
        super(QtWaitForMeasurement, self).__init__(QMessageBox.Question, "Warte auf Messung",
                                                   "Bitte führen sie eine Messung mit dem Tachymeter durch",
                                                   buttons=QMessageBox.Cancel,
                                                   parent=parent)
        self.move(0,0)
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.index = index
        self.timer.timeout.connect(self.pollTachy)
        self.timer.start()

    def pollTachy(self):
        self.data = self.parentWidget().parentWidget().connection.readMeasurement()
        self.parentWidget().parentWidget().log.addPoint(self.data)
        self.timer.stop()
        self.accept()
 
class QtSetStation(QDialog):
    def __init__(self, parent=None):
        super(QtSetStation, self).__init__(parent)
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        self.xField = QLineEdit()
        self.yField = QLineEdit()
        self.zField = QLineEdit()
        self.angleField = QLineEdit()
                
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
        p = (float(self.xField.text()),
             float(self.yField.text()),
             float(self.zField.text()))
        a = float(self.angleField.text())
        self.parentWidget().connection.setStation(p, a)
        super(QtSetStation, self).accept()

class QtGostExportWindow(QDialog):
    def __init__(self, parent=None):
        super(QtGostExportWindow, self).__init__(parent)
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)
        
        self.selectFormat = QComboBox(self)
        for format in self.parentWidget().log.knownFormats:
            self.selectFormat.addItem(format)
        
        self.saveButton = QPushButton("Speichern")
        
        mainLayout.addWidget(QLabel("Format auswählen:"), 0, 0)
        mainLayout.addWidget(self.selectFormat, 0, 1)
        mainLayout.addWidget(self.saveButton, 1,1)
        self.saveButton.clicked.connect(self.save)

    def save(self):
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
        
#class TachyConnect(bpy.types.Operator):
#    bl_idname = "tachy.connect"
#    bl_label = "Connect to Tachymeter"
#    
#    def invoke(self, context, event):
#        return context.window_manager.invoke_props_dialog(self, width=200, height=100)

#    def draw(self, context):
#        scn = bpy.context.scene
#        self.layout.prop_menu_enum(scn, "serialPorts")
#        
#    def execute(self, context):
#        return {"FINISHED"}

#class TACHY_OT_connect(bpy.types.Operator):
#    bl_idname = "tachy.create"
#    bl_label = "connect_tachymeter"
#    
#    def execute(self, context):
#        port = context.scene.serialPorts
#        print("Selected port:", port)
#        context.scene["tachy"] = TachyConnection(port)
#        return {"FINISHED"}

# bpy.types.Scene.tachy = TachyConnection()

# class SelectPortOperator(bpy.types.Operator):
    # bl_idname = "tachy.select_port"
    # bl_label = "Select serial port to connect Tachymeter"
    
    # @classmethod
    # def poll(cls, context):
        # return not bpy.types.Scene.tachy.connected
    
    # def avail_ports(self, context):
        # if sys.platform[:3] == "win":
            # possible = ["COM%i" % i for i in range(1,255)]
        # else:
            # possible = glob("/dev/tty[a-zA-Z]*")
        # ports = []
        # for p in possible:
            # try:
                # serial.Serial(p).close()
            # except serial.SerialException:
                # pass
            # else:
                # ports.append(p)
        # names = ports + ["/dev/pts/5"]
        # ids = ["p%i" % i for i in range(len(names))] 
        # descriptions = names
        # return list(zip(ids, names, descriptions))
        
    # ports = bpy.props.EnumProperty(items=avail_ports, name="Ports")
    
    # def execute(self, context):
        # for i, port, _ in self.avail_ports(context):
            # if i == self.ports:
                # bpy.types.Scene.tachy.open(port)
                # break
        # return {"FINISHED"}

# class StationPoint1(bpy.types.Operator):
    # bl_idname = "tachy.station_point1"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected
    
    # def invoke(self, context, event):
        # return self.execute(context)
        
    # def execute(self, context):
        # context.scene.tachy.stationPoint1(bpy.context.scene.objects.active.location)
        # return {"FINISHED"}

# class AddStationPoint(bpy.types.Operator):
    # bl_idname = "tachy.add_station_point"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected \
               # and len(context.scene.tachy.stationPoint) > 0
    
    # def invoke(self, context, event):
        # context.scene.tachy.stationPointN(bpy.context.scene.objects.active.location)
        # return {"FINISHED"}



# class SetStation(bpy.types.Operator):
    # bl_idname = "tachy.set_station"
    # bl_label = "Set Station"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected \
               # and len(context.scene.tachy.stationPoint) > 2

    # #def getStationPoints(self, context):
    # #    pos, errors = bpy.types.Scene.tachy.computeStation()
    # #    retv = list(zip(["sPoint%i" % i for i in range(len(errors))], 
    # #                    ["(%f, %f, %f); error: %f" % (p[0],p[1],p[2],e) for p,e in zip(bpy.types.Scene.tachy.stationPoint[1:],errors)], 
    # #                    ["" % e for e in errors])
    # #                )
    # #    print(retv)
    # #    return retv

    # #sPointEnum = bpy.props.EnumProperty(items=getStationPoints, name="StaionPoints")

    # def invoke(self, context, event):
        # pos, angle = bpy.types.Scene.tachy.computeStation()
        # bpy.types.Scene.tachy.setStation(pos, angle)
        # return {"FINISHED"}



# class MeasurePoints(bpy.types.Operator):
    # bl_idname = "tachy.measure_points"
    # bl_label = "Measure Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # if not bpy.types.Scene.tachy.connected:
            # return False
        # if not bpy.types.Scene.tachy.stationed:
            # return False

# #        num_selected_vert = 0
# #        for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts :
# #            if v.select:
# #                num_selected_vert += 1
# #        if num_selected_vert != 1:
# #            return False
        # return True
    
    # def invoke(self, context, event):
        # print("start measurement")
        # print(context.window_manager.modal_handler_add(self))
        # self._timer = context.window_manager.event_timer_add(3, context.window)
        
        # return {'RUNNING_MODAL'}
    
    # def modal(self, context, event):
        # if event.type == "ESC":
            # print("stopping measurement")
            # context.window_manager.event_timer_remove(self._timer)
            # return {"FINISHED"}
        # elif event.type == "S" or event.type == "C":
            # #close
            # print("close line")
            # self.close_line()
            # return {"RUNNING_MODAL"}
        # elif event.type == "U" or event.type == "B":
            # #break
            # print("break line")
            # self.break_line()
            # return {"RUNNING_MODAL"}
        # elif event.type == "TIMER":
            # return self.execute(context)
        # return {"PASS_THROUGH"}
    
    # def execute(self, context):
        # try:
            # measurement = context.scene.tachy.readMeasurement(0.1)
            # if measurement is None:
                # print("No measurement")
                # return {"RUNNING_MODAL"}
            # else:
                # print(measurement)
                # x = measurement["targetEast"]
                # y = measurement["targetNorth"]
                # z = measurement["targetHeight"] 
                # bpy.context.area.type='VIEW_3D'
                # if len(bpy.context.selected_objects) == 0:
                    # print("No object selected")
                    # if bpy.context.mode != "OBJECT":
                        # bpy.ops.object.mode_set(mode='OBJECT')
                    # bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(x, y, z))
                    # bpy.ops.object.mode_set(mode='EDIT')
                    # bpy.ops.mesh.delete(type="VERT")
                    # bpy.ops.object.mode_set(mode='OBJECT')
                    # mesh = bpy.context.active_object
                    # mesh.data.vertices.add(1)
                    # mesh.data.vertices[0].co = (0, 0, 0)
                # else:
                    
                    # bpy.ops.object.mode_set(mode='EDIT')
                    # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                    # bpy.context.scene.cursor_location = (x, y, z)
                    # bpy.context.area.type='VIEW_3D'
                    # bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                    # #bpy.context.area.type='TEXT_EDITOR'
                # return {"RUNNING_MODAL"}
        # except TachyError:
            # self.report({"ERROR"}, "Error in tachy communication")

    # def close_line(self):
        # if bpy.context.mode != "EDIT":
                # bpy.ops.object.mode_set(mode='EDIT')
        # b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        # #unselect all vertices
        # for v in b.verts:
            # v.select = False
        # #select first and last vertex
        # b.verts.ensure_lookup_table()
        # b.verts[0].select = True
        # b.verts[-1].select = True
        # #add edge between them
        # bpy.ops.mesh.edge_face_add()
        # #mark edeges for freestyle render (select all edges first)
        # for e in b.edges:
            # e.select=True
        # bpy.ops.mesh.mark_freestyle_edge(clear=False)
        # #fill
        # bpy.ops.mesh.fill()
        # #recalculate normals
        # bpy.ops.mesh.normals_make_consistent()
        # bpy.ops.object.mode_set(mode='OBJECT')
        # #make shading smooth
        # bpy.ops.object.shade_smooth()
        # #unselect the object so the next measurment starts a new mesh
        # bpy.context.object.select = False
        
    # def break_line(self):
        # b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        # #unselect all vertices
        # for v in b.verts:
            # v.select = False
        # #select first and last vertex
        # b.verts[0].select = True
        # b.verts[-1].select = True
        # #add edge between them
        # bpy.ops.mesh.edge_face_add()
        # b.verts[0].select = False
        # b.verts[-1].select = False

# class MeasureNiv(bpy.types.Operator):
    # bl_idname = "tachy.measure_niv"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # def invoke(self, context, event):
        # measurement = context.scene.tachy.readMeasurement()
        # print(measurement)
        # x = measurement["targetEast"]
        # y = measurement["targetNorth"]
        # z = measurement["targetHeight"] 
        
        # bpy.context.scene.cursor_location = (x, y, z)
        
        # strval = "%.2f m NN" % z
        # bpy.ops.object.text_add()
        # ob = bpy.context.object
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
        # ob = bpy.data.objects.new("Triangle", me)
        # #bpy.context.scene.objects.link(ob)
        # ob.location = bpy.context.scene.cursor_location
        # bpy.context.scene.objects.link(ob)
        # #mesh.from_pydata([context.scene.cursor_location], [], [])
        # me.from_pydata(coords, [], faces)
        # me.update()
        # bpy.context.scene.objects.active = ob
        
        # return {"FINISHED"}



# # class MeasureCheckpoint(bpy.types.Operator):
    # # bl_idname = "tachy.measure_checkpoint"
    # # bl_label = "Tachy Panel"
    # # bl_options = {"UNDO"}
    
    # # def invoke(self, context, event):
        # # measurement = context.scene.tachy.readMeasurement()
        # # print(measurement)
        # # x = measurement["targetEast"]
        # # y = measurement["targetNorth"]
        # # z = measurement["targetHeight"] 
        # # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        # # bpy.context.scene.cursor_location = (x, y, z)
        # # bpy.context.area.type='VIEW_3D'
        # # bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        # bpy.context.area.type='TEXT_EDITOR'
        # # return {"FINISHED"}



# class MeasurePanel(bpy.types.Panel):
    # bl_space_type = "VIEW_3D"
    # bl_region_type = "TOOLS"
    # bl_context = "mesh_edit"
    # bl_category = "Tools"
    # bl_label = "Measure Panel"

    # def draw(self, context):
        # layout = self.layout.column(align=True)
        # layout.operator("tachy.measure_points", text="Measure Points")
        
