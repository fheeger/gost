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
    def stationPoint1(self, p):
        self.setPosition(0.0, 0.0)
        self.stationPoint = [p]
        mes = self.readMeasurement()
        self.setAngle(0.0)
        self.stationPointDist = [numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"] ]
        self.stationPointHAngle = [0.0]
        self.stationPointVAngle = [ gon2rad(mes["vertAngle"]) ]
        self.stationPointReflectorH = [ mes["reflectorHeight"] ]
        
    def stationPointN(self, p):
        self.stationPoint.append(p)
        mes = self.readMeasurement()
        self.stationPointDist.append(numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"])
        self.stationPointHAngle.append(gon2rad(mes["hzAngle"]))
        self.stationPointVAngle.append(gon2rad(mes["vertAngle"]))
        self.stationPointReflectorH.append(mes["reflectorHeight"])

    def computeHorizontalPositionAndAngle(self, a, b):
        sA = self.stationPointDist[a]
        sB = self.stationPointDist[b]
        gamma = self.stationPointHAngle[b]
        self.log.write("Distance to A: %f\nDistance to B: %f\n Angle to B: %f(rad) %f(gon)\n" % (sA, sB, gamma, rad2gon(gamma)))


        Ya, Xa, Za = self.stationPoint[a]
        Yb, Xb, Zb = self.stationPoint[b]
        self.log.write("real coordinates\n\tPoint A: %f %f %f\n\tPoint B: %f %f %f\n" % (Ya, Xa, Za, Yb, Xb, Zb))

        sAB = dist(self.stationPoint[a], self.stationPoint[b]) 
        self.log.write("Distance between A and B: %f\n" % sAB)

        tAB = numpy.arctan((Yb - Ya)/(Xb - Xa)) % (2*numpy.pi)
        self.log.write("Angle between sAB and the X axis: %f(rad), %f(gon)\n" % (tAB, rad2gon(tAB)))
        
        alpha = numpy.arccos(min(1, (sA**2+sAB**2-sB**2)/(2*sA*sAB)))
        self.log.write("Alpha: %f(rad), %f(gon)\n" % (alpha, rad2gon(alpha)))
        tAS = tAB + alpha
        self.log.write("tAS: %f(rad), %f(gon)\n" % (tAS, rad2gon(tAS)))

        #wenn der x wer des zweiten punkts kleiner ist als der des ersten muss man subtrahieren
        if Xb < Xa:
            XS = Xa - sA * numpy.cos(tAS)
            YS = Ya - sA * numpy.sin(tAS)
        else:
            XS = Xa + sA * numpy.cos(tAS)
            YS = Ya + sA * numpy.sin(tAS)
        
        if Ya > YS:
            tASN = tAS - numpy.pi
        else:
            tASN = tAS + numpy.pi
        tX = self.getAngle()
        hzAngle = (tASN + tX) % (2*numpy.pi)
            
        return (YS, XS), hzAngle
        
    def computeHeight(self, a):
        g = numpy.sin(numpy.pi/2 - self.stationPointVAngle[a]) * self.stationPointDist[a]

        self.log.write("Computed height difference: %f\n" % (g))
        Za = self.stationPoint[a][2]
        ZS = Za - g + self.stationPointReflectorH[a] - self.getInstrumentHeight()
        self.log.write("Comuted heights: %f\n" % (ZS))
        return ZS
        
    
    def computeStation(self):
        pos_list = []
        angle_list = []
        for b in range(1, len(self.stationPoint)):
            (x, y), angle = self.computeHorizontalPositionAndAngle(0, b)
            z = self.computeHeight(b)
            pos_list.append((x, y, z))
            angle_list.append(angle)
        final_pos = (numpy.mean([point[0] for point in pos_list]),
                     numpy.mean([point[1] for point in pos_list]),
                     numpy.mean([point[2] for point in pos_list]),
                    )
        final_angle = numpy.mean(angle_list)
        error = [dist(final_pos, point) for point in pos_list]
        self.log.write("Position errors:\n\t" + "\n\t".join(map(str, error)) + "\n")
        return final_pos, final_angle#, error
        
    def setStation(self, p, a):
        self.setPosition(p[0], p[1], p[2])
        self.setAngle(a)
        self.stationed = True
            
    
class TachyError(IOError):
    pass
