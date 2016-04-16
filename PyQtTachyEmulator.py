import sys
from glob import glob

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtWidgets import *

import serial

class TachyConnection(QObject):

    def __init__(self, dev=None, baut=4800, lineend="\r\n", log=sys.stderr):
        super(TachyConnection, self).__init__()
        self.log = log
        self.lineend = lineend
        if dev is None:
            self.port = None
        else:
            self.port = serial.Serial(dev, baut)
        self.buffer = ""
        
    def connect(self, dev, baut=4800):
        self.port = serial.Serial(dev, baut)
        
    def readline(self):
        if self.port is None:
            raise NotConnectedError
        line = self.port.readline().decode("ascii")
        self.log.write("READ LINE: %s" % line)
        return line
        
    def write(self, data):
        if self.port is None:
            raise NotConnectedError
        self.log.write("WRITE: %s\n" % repr(data))
        self.port.write(bytes(data, "ascii"))
        
    def read(self, bytes=1, timeout=None):
        if self.port is None:
            raise NotConnectedError
        if not timeout is None:
            self.port.timeout = timeout
        data = self.port.read(bytes).decode("ascii")
        self.log.write("READ: %s\n" % data)
        return data
    
    def readIntoBuffer(self, bytes=100, timeout=0):
        if self.port is None:
            raise NotConnectedError
        if not timeout is None:
            self.port.timeout = timeout
        self.buffer += self.port.read(bytes).decode("ascii")
        if self.buffer.find(self.lineend) != -1:
            self.log.write("buffer: %s\n" % repr(self.buffer))
            tmp = self.buffer[:self.buffer.find(self.lineend)]
            self.buffer = self.buffer[self.buffer.find(self.lineend)+len(self.lineend):]
            return tmp
        return None
            
 
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
        
 
class TachyEmulator(QWidget):
    def __init__(self, dev, parent=None):
        super(TachyEmulator, self).__init__(parent)
 
        self.x = 1.0
        self.y = 2.0
        self.z = 3.0
        self.hzAngle = 4.0
        self.vertAngle = 0.0
        self.instrumentHeight = 1.7
        
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
        stateLayout.addWidget(QLabel("instrument Height:"), 5, 0)
        stateLayout.addWidget(self.instrumentHeightLabel, 5, 1)
        
        self.meassureButton = QPushButton("Meassure Point")
        self.meassureButton.setEnabled(False)


        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.selectPort)
        mainLayout.addLayout(stateLayout)
        mainLayout.addWidget(self.meassureButton)
       
        self.setLayout(mainLayout)
               
        self.setWindowTitle("Tachy Emulator")
        
        self.updateStateDisplay()
        
        self.connection = TachyConnection()
        
        timer = QTimer(self)
        timer.timeout.connect(self.processData) 
        timer.start(100)
        
        self.meassureButton.clicked.connect(self.meassurePoint) 
        self.selectPort.activated[str].connect(self.connect)

        
    def updateStateDisplay(self):
        self.xLabel.setText(str(self.x))
        self.yLabel.setText(str(self.y))
        self.zLabel.setText(str(self.z))
        self.hzAngleLabel.setText(str(self.hzAngle))
        self.vertAngleLabel.setText(str(self.vertAngle))
        self.instrumentHeightLabel.setText(str(self.instrumentHeight))
 
    def processData(self):
        try:
            data = self.connection.readIntoBuffer()
        except NotConnectedError:
            data = None
        if not data is None:
            comArr = data.strip().split("/")
            if comArr[0] == "GET":
                if comArr[2] == "WI21":
                    self.connection.write("*21.322%0+17.d\r\n" % (self.hzAngle * 10**5))
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
                else:
                    self.connection.write("@W127\r\n")
            else:
                self.connection.write("@W127\r\n")
            print("done processing data")
 
    def anyPoint(self, x, y, z, hz, vert, dist, reflectorH=0):
        data = "110006%+017.f 21.322%+017.f 22.322%+017.f 31..00%+017.f 81..00%+017.f 82..00%+017.f 83..00%+017.f 87..10%+017.f" % (self.ptNr, hz*10**5, vert*10**5, dist*10**3, x*10**3, y*10**3, z*10**3, reflectorH*10**3)
        self.connection.write("*%s\r\n" % data)
        self.connection.write("w\r\n")
        answer = self.connection.readIntoBuffer(timeout=1)
        if answer is None:
            QMessageBox.critical(self, "Timeout", "Connection with Blender timed out. Make sure it is waiting for a measurment.")
        elif answer.strip() != "OK":
            QMessageBox.critical(self, "Unexpected Answer from Blender", "Blender answered: %s" % answer)
        else:
            self.ptNr += 1
            print("Messung erfolgreich\n")
            
    def meassurePoint(self):
        meassureWindow = MeassureWindow(self)
        meassureWindow.exec_()
        
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
        #ports.append("/dev/pts/18")
        return ports

    def connect(self, port):
        print("connecting to port: %s" % port)
        self.connection.connect(port)
        self.meassureButton.setEnabled(True)
            
class NotConnectedError(IOError):
    pass

if __name__ == '__main__':
 
    app = QApplication(sys.argv)
 
    screen = TachyEmulator("COM3")
    screen.show()
 
    sys.exit(app.exec_())
