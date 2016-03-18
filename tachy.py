import sys
from glob import glob

import numpy
import serial

from .util import dist, gon2rad, rad2gon

class TachyConnection:
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
            self.port = serial.Serial(port, baut)
        self.baut = baut
        self.log = log
        self.stationed = False
        self.stationPoint = []
        
    def __del__(self):
        try:
            self.port.close()
        except AttributeError:
            #port does not exist or was not open anyway
            pass
            
    def open(self, port, baut=None):
        if not baut is None:
            self.baut = baut
        self.port = serial.Serial(port, self.baut)
    
    def close(self):
        if self.port is None:
            raise TachyError("Not connected")
        self.port.close()
        self.port = None
    
    @property
    def connected(self):
        return not self.port is None
    
    
    def readline(self):
        if self.port is None:
            raise TachyError("Not connected")
        data = self.port.readline().decode("ascii")
        if len(data) == 0:
            raise Timeout("Timeout during readline")
        self.log.write("READ LINE: %s\n" % data)
        return data
    
    def read(self, size=1):
        if self.port is None:
            raise TachyError("Not connected")
        data = self.port.read(size).decode("ascii")
        if len(data) < size:
            raise Timeout("Timeout during read")
        self.log.write("READ: %s\n" % data)
        return data
        
    def write(self, data):
        if self.port is None:
            raise TachyError("Not connected")
        d = bytes(data, "latin-1")
        self.log.write("WRITE: %s\n" % d)
        written = self.port.write(d)
        if written < len(data):
            raise Timeout("Timeout during write")


    def readMeasurement(self, timeout=None):
        try:
            if self.port is None:
                raise TachyError("Not connected")
            if not timeout is None:
                oldTimeout = self.port.timeout
                self.port.timeout = timeout
                star = self.read(1)
                self.port.timeout = oldTimeout
                if len(star) == 0:
                    #timeout occured
                    return None
                if star != "*":
                    raise TachyError("Unexpected character at start of measurement: '%s'" % star)
                mStr = self.readline().strip()
            else:
                #if no 
                mStr = self.readline()[1:].strip()
            data_point = {}
            lines = mStr.split(" ")
            for line in lines:
                word_index = line[0:2]
                data_info = line[3:6]
                data = line[6:]
                if word_index in self.digits:
                    data_point[self.codes[word_index]] = float(data)/10**self.digits[word_index]
                else:
                    data_point[self.codes[word_index]] = data
            secondLine = self.readline().strip()
            if secondLine != "w":
                raise TachyError("Unexpected character at end of measurement: '%s'" % secondLine)
            self.write("OK\r\n")
            return data_point
        except Exception as e:
            raise TachyError(e.args)

    
    def setPosition(self, x, y, z=None):
        self.write("PUT/84...0"+ "%0+17.d \r\n" % (x*10**self.digits["84"])) #easting -> x
        if self.readline().strip() != "?":
            raise TachyError()
        self.write("PUT/85...0"+ "%0+17.d \r\n" % (y*10**self.digits["85"])) #northing -> y
        if self.readline().strip() != "?":
            raise TachyError()
        if not z is None:
            self.write("PUT/86...0"+ "%0+17.d \r\n" % (z*10**self.digits["86"])) #height -> z
            if self.readline().strip() != "?":
                raise TachyError()
            
    def setAngle(self, alpha):
        self.write("PUT/21...2"+ "%0+17.d \r\n" % (alpha*10**self.digits["21"]))
        if self.readline().strip() != "?":
            raise TachyError()
            
    def getAngle(self):
        self.write("GET/M/WI21\r\n")
        
        line = self.readline().strip()
        if line[0] != "*":
            raise TachyError()
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getReflectorHeight(self):
        self.write("GET/M/WI87\r\n")  
        line = self.readline().strip()
        if line[0] != "*":
            raise TachyError()
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getInstrumentHeight(self):
        self.write("GET/M/WI88\r\n")  
        line = self.readline().strip()
        if line[0] != "*":
            raise TachyError()
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]
        
    def beep(self):
        self.write("BEEP/0\r\n")
        if self.readline().strip() != "?":
            raise TachyError
            
    #free stationing
    def stationPoint1(self, p, timeout=60):
        oldTimeout = self.port.timeout
        self.port.timeout = timeout
        self.port.write_timout = timeout
        self.setPosition(0.0, 0.0)
        self.stationPoint = [p]
        
        mes = self.readMeasurement()
        self.setAngle(0.0)
        self.stationPointDist = [numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"] ]
        self.stationPointHAngle = [0.0]
        self.stationPointVAngle = [ gon2rad(mes["vertAngle"]) ]
        try:
            self.stationPointReflectorH = [ mes["reflectorHeight"] ]
        except KeyError:
            self.stationPointReflectorH = [self.getReflectorHeight()]
        self.port.write_timout = oldTimeout
        self.port.timeout = oldTimeout
        
    def stationPointN(self, p, timeout=60):
        oldTimeout = self.port.timeout
        self.port.timeout = timeout
        self.port.write_timout = timeout
        self.stationPoint.append(p)
        mes = self.readMeasurement()
        self.stationPointDist.append(numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"])
        self.stationPointHAngle.append(gon2rad(mes["hzAngle"]))
        self.stationPointVAngle.append(gon2rad(mes["vertAngle"]))
        try:
            self.stationPointReflectorH.append(mes["reflectorHeight"])
        except KeyError:
            self.stationPointReflectorH.append(self.getReflectorHeight())
        self.port.write_timout = oldTimeout
        self.port.timeout = oldTimeout

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
        oldTimeout = self.port.timeout
        self.port.timeout = timeout
        self.port.write_timout = timeout
        (x, y), rotation, error = self.computeHorizontalPositionAndAngle()
        z = self.computeHeight(0)
        self.log.write("Position error: %f\n" % error)
        self.log.write("Rotation: %f\n" % rotation)
        self.port.timeout = oldTimeout
        return (x, y, z), rotation#, error
        

    def setStation(self, p, a, timeout=60):
        oldTimeout = self.port.timeout
        self.port.timeout = timeout
        self.port.write_timout = timeout
        print("setting station")
        self.setPosition(p[0], p[1], p[2])
        self.log.write("Position: %f, %f, %f\n" % p)
        currentAngle = self.getAngle()
        self.log.write("current angle: %f gon\n" % currentAngle)
        self.log.write("rotation angle: %f gon\n" % rad2gon(a))
        self.setAngle((currentAngle + rad2gon(a)) % 400)
        self.stationed = True
        self.port.write_timout = oldTimeout
        self.port.timeout = oldTimeout
            
    
class TachyError(IOError):
    pass
    
class Timeout(IOError):
    pass
