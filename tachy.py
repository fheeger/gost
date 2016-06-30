import sys
import time
from glob import glob

import numpy
from PyQt5 import QtSerialPort
from PyQt5.QtCore import QIODevice

from .util import dist, gon2rad, rad2gon

class TachyConnection:
    le    = "\r\n"
    
    codes = {"11": "ptid",
             "21": "hzAngle",
             "22": "vertAngle",
             "31": "slopeDist",
             "81": "targetEast",
             "82": "targetNorth",
             "83": "targetHeight",
             "87": "reflectorHeight",
             "88": "instrumentHeight",
             }
             
    digits = {"21": 5,
              "22": 5,
              "31": 3,
              "81": 3,
              "82": 3,
              "83": 3,
              "84": 3,
              "85": 3,
              "86": 3,
              "87": 3,
              "88": 3,
              }

    def __init__(self, port=None, baut=4800, log=sys.stderr):
        if port is None:
            self.port = None
        else:
            self.open(port, baut)
        self.baut = baut
        self.timeout = 0.5
        self.writeTimeout = 1
        self.log = log
        self.stationed = False
        self.stationPoint = []
        self.lineBuffer = []
        self.buffer = ""
        
    def __del__(self):
        try:
            self.port.close()
        except AttributeError:
            #port does not exist or was not open anyway
            pass
            
    def open(self, port, baut=None):
        if not baut is None:
            self.baut = baut
        self.port = QtSerialPort.QSerialPort(port)
        self.port.open(QIODevice.ReadWrite)
        self.port.setBaudRate(self.baut)
    
    def close(self):
        if self.port is None:
            raise TachyError("Not connected")
        self.port.close()
        self.port = None
    
    @property
    def connected(self):
        return not self.port is None
    
    
    def readLines(self, n=2):
        self.buffer += bytes(self.port.readAll()).decode("ascii")
        #print("addinf data to buffer: %s" % repr(self.buffer))
        pos = self.buffer.find(self.le)
        while pos > 0:
            self.lineBuffer.append(self.buffer[:pos])
            print("adding data to line buffer: %s" % repr(self.buffer[:pos]))
            self.buffer = self.buffer[pos+len(self.le):]
            pos = self.buffer.find(self.le)
        
        if len(self.lineBuffer) == n:
            tmp = self.lineBuffer
            self.lineBuffer = []
            print("returning: %s" % tmp)
            return tmp
        return None
    
    def readline(self):
        if self.port is None:
            raise TachyError("Not connected")
        if not self.port.canReadLine():
            raise ValueError("No full line is available")
        data = bytes(self.port.readLine()).decode("ascii")
        self.log.write("READ LINE: %s\n" % data)
        return data
    
    def read(self, size=1):
        if self.port is None:
            raise TachyError("Not connected")
        data = self.port.read(size).decode("ascii")
        self.log.write("READ: %s\n" % data)
        return data
        
    def write(self, data):
        if self.port is None:
            raise TachyError("Not connected")
        d = bytes(data, "latin-1")
        self.log.write("WRITE: %s\n" % d)
        self.port.write(d)
        self.port.flush()
        if not self.port.waitForBytesWritten(self.writeTimeout*1000):
            raise Timeout("Timeout during write")

    def readMeasurement(self):
        if self.port is None:
            raise TachyError("Not connected")
        
        lines = self.readLines(2)

        if lines is None:
            return None
            
        rawStr = lines[0].strip()
        mStr = rawStr[1:]
        if rawStr[0] != "*":
            raise TachyError("Unexpected character at start of measurement: '%s'" % rawStr[0])

            
        data_point = {}
        if not mStr:
            return None
        words = mStr.split(" ")
        for word in words:
            word_index = word[0:2]
            data_info = word[3:6]
            data = word[6:]
            if word_index in self.digits:
                data_point[self.codes[word_index]] = float(data)/10**self.digits[word_index]
            else:
                data_point[self.codes[word_index]] = data
        secondLine = lines[1].strip() 
        if secondLine != "w":
            raise TachyError("Unexpected character at end of measurement: '%s'" % secondLine)
        self.write("OK\r\n")
        return data_point


    
    def setPosition(self, x, y, z=None):
       
        self.write("PUT/84...0"+ "%0+17.d \r\n" % (x*10**self.digits["84"])) #easting -> x
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
        self.write("PUT/85...0"+ "%0+17.d \r\n" % (y*10**self.digits["85"])) #northing -> y
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
        if not z is None:
            self.write("PUT/86...0"+ "%0+17.d \r\n" % (z*10**self.digits["86"])) #height -> z
            lines = None
            while lines is None:
                self.port.waitForReadyRead(500)
                lines = self.readLines(1)
            line = lines[0]
            if line.strip() != "?":
                    raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
      
    def getPosition(self):
        self.write("GET/M/WI84\r\n")    #problem : does not return x
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        if data[1]!="W":
            xpos=float(data)/10**self.digits[word_index]
        else:
            xpos=0 
        self.write("GET/M/WI85\r\n")    #problem : does not return y
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        if data[1]!="W":
            ypos=float(data)/10**self.digits[word_index]
        else:
            ypos=0
        self.write("GET/M/WI86\r\n")    #problem : does not return z
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        if data[1]!="W":
            zpos=float(data)/10**self.digits[word_index]
        else:
            zpos=0
        return (xpos,ypos,zpos)

    def setAngle(self, alpha):
        self.write("PUT/21...2"+ "%0+17.d \r\n" % (alpha*10**self.digits["21"]))
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
            
    def getAngle(self):
        self.write("GET/M/WI21\r\n")
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getReflectorHeight(self):
        self.write("GET/M/WI87\r\n")  
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getInstrumentHeight(self):
        self.write("GET/M/WI88\r\n")  
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]
        
    def beep(self):
        self.write("BEEP/0\r\n")
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
            
    #free stationing
    def stationPoint1(self, p, measurement=None, timeout=60):
        self.setPosition(0.0, 0.0)
        self.stationPoint = [p]
        if measurement is None:
            print("no measurment for point 1. Starting measurment.")
            oldTimeout = self.timeout
            self.timeout = timeout
            self.port.write_timout = timeout
            mes = self.readMeasurement()
        else:
            mes = measurement
        #self.setAngle(0.0)
        self.stationPointDist = [numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"] ]
        self.stationPointHAngle = [gon2rad(mes["hzAngle"])]
        self.stationPointVAngle = [gon2rad(mes["vertAngle"])]
        try:
            self.stationPointReflectorH = [ mes["reflectorHeight"] ]
        except KeyError:
            self.stationPointReflectorH = [self.getReflectorHeight()]
        if measurement is None:
            self.port.write_timout = oldTimeout
            self.timeout = oldTimeout
        
    def stationPointN(self, p, measurement=None, timeout=60):
        self.stationPoint.append(p)
        if measurement is None:
            oldTimeout = self.timeout
            self.timeout = timeout
            self.port.write_timout = timeout
            mes = self.readMeasurement()
        else:
            mes = measurement
        self.stationPointDist.append(numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"])
        self.stationPointHAngle.append(gon2rad(mes["hzAngle"]))
        self.stationPointVAngle.append(gon2rad(mes["vertAngle"]))
        try:
            self.stationPointReflectorH.append(mes["reflectorHeight"])
        except KeyError:
            self.stationPointReflectorH.append(self.getReflectorHeight())
        if measurement is None:
            self.port.write_timout = oldTimeout
            self.timeout = oldTimeout

    def computeHorizontalPositionAndAngle(self):
        #number of points
        n = len(self.stationPoint)
        #extract coordinates in target co-system
        X = numpy.array([p[0] for p in self.stationPoint])
        Y = numpy.array([p[1] for p in self.stationPoint])
        self.log.write("Coordinates in target co-system:\n")
        for i in range(n):
            self.log.write("\tX:%f, Y:%f\n" % (X[i], Y[i]))
        #compute coordinates in source co-system
        x = numpy.array([0.0]*n)
        y = numpy.array([0.0]*n)
        for p in range(n):
            x[p] = self.stationPointDist[p] * numpy.sin(self.stationPointHAngle[p])
            y[p] = self.stationPointDist[p] * numpy.cos(self.stationPointHAngle[p])
        self.log.write("Coordinates in source co-system:\n")
        for i in range(n):
            self.log.write("\tx:%f, y:%f\n" % (x[i], y[i]))
        #compute center in both co-sys
        self.log.write("Center of Mass\n")
        #source co-sys
        x_s = numpy.sum(x)/n
        y_s = numpy.sum(y)/n
        self.log.write("\tsource co-sys: x_s:%f, y_s:%f\n" % (x_s, y_s))
        #target co-sys
        X_s = numpy.sum(X)/n
        Y_s = numpy.sum(Y)/n
        self.log.write("\ttarget co-sys: X_s:%f, Y_s:%f\n" % (X_s, Y_s))
        #reduction onto the center
        x_bar = x - x_s
        y_bar = y - y_s
        self.log.write("Reduced coordinates in source co-system:\n")
        for i in range(n):
            self.log.write("\tx_bar:%f, y_bar:%f\n" % (x_bar[i], y_bar[i]))
        X_bar = X - X_s
        Y_bar = Y - Y_s
        self.log.write("Reduced coordinates in target co-system:\n")
        for i in range(n):
            self.log.write("\tX_bar:%f, X_bar:%f\n" % (X_bar[i], Y_bar[i]))
        #compute transforamtion parameters
        self.log.write("Transformation parameters:\n")
        N = (numpy.sum(x_bar**2) * numpy.sum(y_bar**2)) - (numpy.sum(x_bar*y_bar))**2
        
        a1 = (numpy.sum(x_bar*X_bar) * numpy.sum(y_bar**2) - numpy.sum(y_bar*X_bar) * numpy.sum(x_bar*y_bar)) / N
        a2 = (numpy.sum(x_bar*X_bar) * numpy.sum(x_bar*y_bar) - numpy.sum(y_bar*X_bar) * numpy.sum(x_bar**2)) / N
        a3 = (numpy.sum(y_bar*Y_bar) * numpy.sum(x_bar**2) - numpy.sum(x_bar*Y_bar) * numpy.sum(x_bar*y_bar)) / N
        a4 = (numpy.sum(x_bar*Y_bar) * numpy.sum(y_bar**2) - numpy.sum(y_bar*Y_bar) * numpy.sum(x_bar*y_bar)) / N
        
        Y0 = Y_s - a3*y_s - a4*x_s
        X0 = X_s - a1*x_s + a2*y_s
        
        self.log.write("\ta1: %f\n" % a1)
        self.log.write("\ta2: %f\n" % a2)
        self.log.write("\ta3: %f\n" % a3)
        self.log.write("\ta3: %f\n" % a3)
        
        self.log.write("\tX0: %f\n" % X0)
        self.log.write("\tY0: %f\n" % Y0)
        #computation of rotation angles
        self.log.write("Rotation Angles:\n")
        #abszisse, x-axis
        alpha = numpy.arctan(a4/a1)
        #ordinate, y-axis
        beta = numpy.arctan(a2/a3)
        self.log.write("\talpha: %f gon\n" % rad2gon(alpha))
        self.log.write("\tbeta: %f gon\n" % rad2gon(beta))
        
        #compute scales
        m1 = numpy.sqrt(a1**2 + a4**2)
        m2 = numpy.sqrt(a2**2 + a3**2)
        
        #errors
        W_Y = -Y0 - a3*y - a4*x + Y
        W_X = -X0 - a1*x + a2*y + X
        self.log.write("Errors:\n")
        for i in range(len(W_X)):
            self.log.write("\tW_X[%i]: %f, W_Y[%i]: %f\n" % (i, W_X[i], i, W_Y[i]))
        
        #precission
        s = numpy.sqrt(abs((numpy.sum(W_X*W_X) + numpy.sum(W_X*W_Y))) / (2*n - 6))
        self.log.write("Precission: %f\n" % s)
        
        #
        if Y0 > Y[0]:
            self.log.write("first station point lower than station\n")
            angle = numpy.pi - beta
        else:
            angle = -beta
        self.log.write("angle: %f\n" % angle)
        return (X0, Y0), angle, s
        
    def computeHeight(self, a):
        g = numpy.sin(numpy.pi/2 - self.stationPointVAngle[a]) * self.stationPointDist[a]

        self.log.write("Computed height difference: %f\n" % (g))
        Za = self.stationPoint[a][2]
        ZS = Za - g + self.stationPointReflectorH[a] - self.getInstrumentHeight()
        self.log.write("Comuted heights: %f\n" % (ZS))
        return ZS
        
    
    def computeStation(self, timeout=60):
        oldTimeout = self.timeout
        self.timeout = timeout
        self.writeTimout = timeout
        (x, y), rotation, error = self.computeHorizontalPositionAndAngle()
        z = self.computeHeight(0)
        self.log.write("Position error: %f\n" % error)
        self.log.write("Rotation: %f\n" % rotation)
        self.timeout = oldTimeout
        return (x, y, z), rotation, error
        

    def setStation(self, p, a, timeout=60):
       
        oldTimeout = self.timeout
        self.timeout = timeout
        self.writeTimeout = timeout
        print("setting station")
        self.log.write("Position: %f, %f, %f\n" % p)
        self.setPosition(p[0], p[1], p[2])
        self.log.write("setting angle to: %f gon\n" % a)
        self.setAngle(a)
        self.stationed = True
        self.timeout = oldTimeout
            
    
class TachyError(IOError):
    pass
    
class Timeout(IOError):
    pass
