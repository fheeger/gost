import sys, random, time
from glob import glob

import numpy

from PyQt5.QtCore import QObject, QTimer, QIODevice
from PyQt5.QtWidgets import *
from PyQt5 import QtSerialPort

class TachyConnection(QObject):

    def __init__(self, dev=None, baut=4800, lineend="\r\n", timeout=3, log=sys.stderr):
        super(TachyConnection, self).__init__()
        self.log = log
        self.lineend = lineend
        if dev is None:
            self.port = None
        else:
            sel.connect(dev, baut)
        self.buffer = ""
        self.lineBuffer = []
        self.timeout = timeout
        
    def connect(self, dev, baut=4800):
        self.port = QtSerialPort.QSerialPort(dev)
        self.port.open(QIODevice.ReadWrite)
        self.port.setBaudRate(baut)
        
    def readline(self):
        if self.port is None:
            raise NotConnectedError
        if self.port.waitForReadyRead(self.timeout*1000):
            line = self.port.readLine().decode("ascii")
            self.log.write("READ LINE: %s" % line)
            return line
        raise TimeoutError("time out while reading line")
    
    def readLines(self, n=2):
        self.buffer += bytes(self.port.readAll()).decode("ascii")
        #print("addinf data to buffer: %s" % repr(self.buffer))
        pos = self.buffer.find(self.lineend)
        while pos > 0:
            self.lineBuffer.append(self.buffer[:pos])
            print("adding data to line buffer: %s" % repr(self.buffer[:pos]))
            self.buffer = self.buffer[pos+len(self.lineend):]
            pos = self.buffer.find(self.lineend)
        
        if len(self.lineBuffer) == n:
            tmp = self.lineBuffer
            self.lineBuffer = []
            print("returning: %s" % tmp)
            return tmp
        return None
    
    def write(self, data):
        if self.port is None:
            raise NotConnectedError
            
        self.log.write("WRITE: %s\n" % repr(data))
        self.port.write(bytes(data, "ascii"))
        self.port.flush()
        if not self.port.waitForBytesWritten(self.timeout*1000):
            raise TimeoutError("time out while writing")
        
    def read(self, bytes=1, timeout=None):
        if self.port is None:
            raise NotConnectedError
        if not timeout is None:
            self.port.timeout = timeout
        if self.port.waitForReadyRead(self.timeout*1000):      
            data = self.port.read(bytes).decode("ascii")
            self.log.write("READ: %s\n" % data)
            return data
        raise TimeoutError("time out while reading")
     
 
class MeassureWindow(QDialog):
    def __init__(self, parent):
        super(MeassureWindow, self).__init__(parent)
        
        self.xField = QLineEdit()
        self.xField.setText("0")
        self.yField = QLineEdit()
        self.yField.setText("0")
        self.zField = QLineEdit()
        self.zField.setText("0")
        self.hzField = QLineEdit()
        self.hzField.setText("0")
        self.vertField = QLineEdit()
        self.vertField.setText("0")
        self.distField = QLineEdit()
        self.distField.setText("0")
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel("x:"), 0, 0)
        mainLayout.addWidget(self.xField , 0, 1)
        mainLayout.addWidget(QLabel("y:"), 1, 0)
        mainLayout.addWidget(self.yField, 1, 1)
        mainLayout.addWidget(QLabel("z:"), 2, 0)
        mainLayout.addWidget(self.zField, 2, 1)
        mainLayout.addWidget(QLabel("horizontal Angle:"), 3, 0)
        mainLayout.addWidget(self.hzField, 3, 1)
        mainLayout.addWidget(QLabel("vertical Angle:"), 4, 0)
        mainLayout.addWidget(self.vertField, 4, 1)
        mainLayout.addWidget(QLabel("Distance:"), 5, 0)
        mainLayout.addWidget(self.distField, 5, 1)
        
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Cancel")
        
        mainLayout.addWidget(self.okButton)
        mainLayout.addWidget(self.cancleButton)
        
        self.setLayout(mainLayout)
               
        self.setWindowTitle("Meassure Point")
        
        self.okButton.clicked.connect(self.accept) 
        self.cancleButton.clicked.connect(self.reject)
        
    def accept(self):
        self.parent().anyPoint(float(self.xField.text()), 
                               float(self.yField.text()), 
                               float(self.zField.text()),
                               float(self.hzField.text()),
                               float(self.vertField.text()),
                               float(self.distField.text())
                              )
        super(MeassureWindow, self).accept()
        
class RandomCircleWindow(QDialog):
    def __init__(self, parent):
        super(RandomCircleWindow, self).__init__(parent)
        
        self.xField = QLineEdit()
        self.xField.setText("0")
        self.yField = QLineEdit()
        self.yField.setText("0")
        self.zField = QLineEdit()
        self.zField.setText("0")
        self.rField = QLineEdit()
        self.rField.setText("3")
        self.nField = QLineEdit()
        self.nField.setText("20")
        self.hField = QLineEdit()
        self.hField.setText("0")
        self.meassureButton = QPushButton("Meassure")
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel("Circle center x:"), 0, 0)
        mainLayout.addWidget(self.xField , 0, 1)
        mainLayout.addWidget(QLabel("Circle center y:"), 1, 0)
        mainLayout.addWidget(self.yField , 1, 1)
        mainLayout.addWidget(QLabel("Circle center z:"), 2, 0)
        mainLayout.addWidget(self.zField , 2, 1)
        mainLayout.addWidget(QLabel("Circle radius:"), 3, 0)
        mainLayout.addWidget(self.rField , 3, 1)
        mainLayout.addWidget(QLabel("Number of points:"), 4, 0)
        mainLayout.addWidget(self.nField , 4, 1)
        mainLayout.addWidget(QLabel("Circle height:"), 5, 0)
        mainLayout.addWidget(self.hField , 5, 1)
        
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Cancel")
        
        mainLayout.addWidget(self.okButton)
        mainLayout.addWidget(self.cancleButton)
        
        self.setLayout(mainLayout)
        
        self.okButton.clicked.connect(self.accept) 
        self.cancleButton.clicked.connect(self.reject)
        
    def accept(self):
        x = float(self.xField.text())
        y = float(self.yField.text())
        z = float(self.zField.text())
        r = float(self.rField.text())
        n = int(self.nField.text())
        h = float(self.hField.text())
        self.measureRandomPolyCircle(x,y,z,r,n,h)
        super(RandomCircleWindow, self).accept()
        
    def measureRandomPolyCircle(self, x0=0, y0=0, z0=0, r=3, n=20, h=2):
        angles = []
        for i in range(n):
            angles.append(random.uniform(0, 2*numpy.pi))
        angles.sort()
        for a in angles:
            x = x0 + r*numpy.cos(a)
            y = y0 + r*numpy.sin(a)
            z = z0 + random.uniform(0, h)
            self.parentWidget().anyPoint(x, y, z, a, 0, r)
            time.sleep(0.5)
        
class TachyEmulator(QWidget):
    def __init__(self, dev, parent=None):
        super(TachyEmulator, self).__init__(parent)
 
        self.x = 1.0
        self.y = 2.0
        self.z = 3.0
        self.hzAngle = 4.0
        self.vertAngle = 0.0
        self.instrumentHeight = 1.7
        self.reflectorHeight = 1.5
        
        self.ptNr = 0
        
        self.selectPort = QComboBox(self)
        for port in self.avail_ports():
            self.selectPort.addItem(port)
        
        #display current state
        self.xLabel = QLabel("")
        self.yLabel = QLabel("")
        self.zLabel = QLabel("")
        self.hzAngleLabel = QLabel("")
        self.vertAngleLabel = QLabel("")
        self.reflectorHeightLabel = QLabel("")
        self.instrumentHeightLabel = QLabel("")
        stateLayout = QGridLayout()
        
        stateLayout.addWidget(QLabel("x:"), 0, 0)
        stateLayout.addWidget(self.xLabel, 0, 1)
        stateLayout.addWidget(QLabel("y:"), 1, 0)
        stateLayout.addWidget(self.yLabel, 1, 1)
        stateLayout.addWidget(QLabel("z:"), 2, 0)
        stateLayout.addWidget(self.zLabel, 2, 1)
        stateLayout.addWidget(QLabel("horizontal Angle:"), 3, 0)
        stateLayout.addWidget(self.hzAngleLabel, 3, 1)
        stateLayout.addWidget(QLabel("vertical Angle:"), 4, 0)
        stateLayout.addWidget(self.vertAngleLabel, 4, 1)
        stateLayout.addWidget(QLabel("reflector Height:"), 5, 0)
        stateLayout.addWidget(self.reflectorHeightLabel, 5, 1)
        stateLayout.addWidget(QLabel("instrument Height:"), 6, 0)
        stateLayout.addWidget(self.instrumentHeightLabel, 6, 1)
        
        self.meassureButton = QPushButton("Meassure Point")
        self.circleButton = QPushButton("Meassure random circle")
        self.meassureButton.setEnabled(False)
        self.circleButton.setEnabled(False)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.selectPort)
        mainLayout.addLayout(stateLayout)
        mainLayout.addWidget(self.meassureButton)
        mainLayout.addWidget(self.circleButton)
       
        self.setLayout(mainLayout)
               
        self.setWindowTitle("Tachy Emulator")
        
        self.updateStateDisplay()
        
        self.connection = TachyConnection()
        
        self.meassureButton.clicked.connect(self.meassurePoint) 
        self.circleButton.clicked.connect(self.measureRandomPolyCircle)
        self.selectPort.activated[str].connect(self.connect)
        
        
    def updateStateDisplay(self):
        self.xLabel.setText(str(self.x))
        self.yLabel.setText(str(self.y))
        self.zLabel.setText(str(self.z))
        self.hzAngleLabel.setText(str(self.hzAngle))
        self.vertAngleLabel.setText(str(self.vertAngle))
        self.reflectorHeightLabel.setText(str(self.reflectorHeight))
        self.instrumentHeightLabel.setText(str(self.instrumentHeight))
 
    def processData(self):
        print("processing data")
        data = self.connection.readLines(1)[0]
        print(data)
        if not data is None:
            comArr = data.strip().split("/")
            if comArr[0] == "GET":
                if comArr[2] == "WI21":
                    self.connection.write("*21.322%0+17.d\r\n" % (self.hzAngle * 10**5))
                elif comArr[2] == "WI84":
                    self.connection.write("*84.322%0+17.d\r\n" % (self.x * 10**3)) 
                elif comArr[2] == "WI85":
                    self.connection.write("*85.322%0+17.d\r\n" % (self.y * 10**3))
                elif comArr[2] == "WI86":
                    self.connection.write("*86.322%0+17.d\r\n" % (self.z * 10**3))
                elif comArr[2] == "WI87":
                    self.connection.write("*87.322%0+17.d\r\n" % (self.reflectorHeight * 10**3))
                elif comArr[2] == "WI88":
                    self.connection.write("*88.322%0+17.d\r\n" % (self.instrumentHeight * 10**3))
                else:
                    self.connection.write("@W127\r\n")
            elif comArr[0] == "PUT":
                if comArr[1][:2] == "21":
                    self.hzAngle = float(comArr[1][-17:]) / 10**5
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                elif comArr[1][:2] == "84":
                    self.x = float(comArr[1][-17:]) / 10**3
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                elif comArr[1][:2] == "85":
                    self.y = float(comArr[1][-17:]) / 10**3
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                elif comArr[1][:2] == "86":
                    self.z = float(comArr[1][-17:]) / 10**3
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                elif comArr[1][:2] == "87":
                    self.reflectorHeight = float(comArr[1][-17:]) / 10**3
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                elif comArr[1][:2] == "88":
                    self.instrumentHeight = float(comArr[1][-17:]) / 10**3
                    self.updateStateDisplay()
                    self.connection.write("?\r\n")
                else:
                    print("could not process data: " + data)
                    self.connection.write("@W127\r\n")
            else:
                print("could not process data: " + data)
                self.connection.write("@W127\r\n")
            print("done processing data")
 
    def anyPoint(self, x, y, z, hz, vert, dist, reflectorH=0):
        self.connection.port.readyRead.disconnect()
        data = "110006%+017.f 21.322%+017.f 22.322%+017.f 31..00%+017.f 81..00%+017.f 82..00%+017.f 83..00%+017.f 87..10%+017.f" % (self.ptNr, hz*10**5, vert*10**5, dist*10**3, x*10**3, y*10**3, z*10**3, reflectorH*10**3)
        self.connection.write("*%s\r\n" % data)
        self.connection.write("w\r\n")
        lines = None
        while lines is None:
            self.connection.port.waitForReadyRead(500)
            lines = self.connection.readLines(1)
        answer = lines[0]
        self.connection.port.readyRead.connect(self.processData)
        if answer.strip() != "OK":
            QMessageBox.critical(self, "Unexpected Answer from Blender", "Blender answered: %s" % answer)
        else:
            self.ptNr += 1
            print("Messung erfolgreich\n")
            
    
    def meassurePoint(self):
        meassureWindow = MeassureWindow(self)
        meassureWindow.exec_()
        
    def measureRandomPolyCircle(self):
        circleWindow = RandomCircleWindow(self)
        circleWindow.exec_()
    
    def avail_ports(self):
        return [p.portName() for p in QtSerialPort.QSerialPortInfo.availablePorts() if not p.isBusy()]

    def connect(self, port):
        print("connecting to port: %s" % port)
        self.connection.connect(port)
        self.meassureButton.setEnabled(True)
        self.circleButton.setEnabled(True)
        self.connection.port.readyRead.connect(self.processData)
            
class NotConnectedError(IOError):
    pass

if __name__ == '__main__':
 
    app = QApplication(sys.argv)
 
    screen = TachyEmulator("COM3")
    screen.show()
 
    sys.exit(app.exec_())
