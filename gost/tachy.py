import sys
from glob import glob

import numpy
import serial


class TachyConnection:
    codes = {"11": "ptid",
             "21": "hzAngle",
             "22": "vertAngle",
             "31": "slopeDist",
             "81": "targetEast",
             "82": "targetNorth",
             "83": "targetHeight",
             "87": "reflectorHeight",
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
              }

    def __init__(self, port=None, baut=4800, log=sys.stderr):
        if port is None:
            self.port = None
        else:
            self.port = serial.Serial(port, baut)
        self.baut = baut
        self.log = log
        
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
        d = bytes(data, "ascii")
        self.log.write("WRITE: %s\n" % d)
        self.port.write(d)

    def readMeasurment(self):
        data_point = {}
        mStr = self.readline()[1:].strip()
        lines = mStr.split(" ")
        for line in lines:
            word_index = line[0:2]
            data_info = line[3:6]
            data = line[6:]
            if word_index in self.digits:
                data_point[self.codes[word_index]] = float(data)/10**self.digits[word_index]
            else:
                data_point[self.codes[word_index]] = data
        if self.readline().strip() != "w":
            raise TachyError()
        self.write("OK\r\n")
        return data_point
    
    def readMeasurement(self, timeout=None):
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
                raise TachyError("Unexpected character at start of measurment: '%s'" % star)
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
            raise TachyError("Unexpected character at end of measurment: '%s'" % secondLine)
        self.write("OK\r\n")
        return data_point
        
    
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

    def beep(self):
        self.write("BEEP/0\r\n")
        if self.readline().strip() != "?":
            raise TachyError

class TachyError(IOError):
    pass
