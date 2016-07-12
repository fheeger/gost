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
import time
from glob import glob

import numpy
from PyQt5 import QtSerialPort
from PyQt5.QtCore import QIODevice

from .util import dist, gon2rad, rad2gon

class TachyConnection:
    """Class to managa a serial connection to a Tachymeter.
    
    For now this only supports Leica devices.
    """
    
    #which line ending is used
    #this should be changeable by the user
    le    = "\r\n"
    
    #mapping Leica codes to field names
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
    
    #mapping leica codes to the number of decimal digits 
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
        """Constructor"""
        
        #if a port name was given open it
        if port is None:
            self.port = None
        else:
            self.open(port, baut)
        #save the connection options
        self.baut = baut
        self.timeout = 0.5
        self.writeTimeout = 1
        self.log = log
        #additional members to save stationing data
        self.stationed = False
        self.stationPoint = []
        #buffers for reading data
        self.lineBuffer = []
        self.buffer = ""
        
    def __del__(self):
        try:
            self.port.close()
        except AttributeError:
            #port does not exist or was not open anyway
            pass
            
    def open(self, port, baut=None):
        """Open a serial connection on the given port."""
        
        if not baut is None:
            self.baut = baut
        #create a port object
        self.port = QtSerialPort.QSerialPort(port)
        #open the connection and set the baudrate
        self.port.open(QIODevice.ReadWrite)
        self.port.setBaudRate(self.baut)
    
    def close(self):
        """Close open serial connection."""
        if self.port is None:
            raise TachyError("Not connected")
        self.port.close()
        self.port = None
    
    @property
    def connected(self):
        return not self.port is None
    
    
    def readLines(self, n=2):
        """Read n lines from the serial connection.
        
        Will return a string with n lines or None if not enough 
        data is recieved on the serial port. Data will be moved line
        wise from the buffer to the lineBuffer. Data that is not returned
        wills stay in the buffer for the next function call.
        """
        
        #read all available data from the serial port into the buffer
        self.buffer += bytes(self.port.readAll()).decode("ascii")
        #print("adding data to buffer: %s" % repr(self.buffer))
        #find the first occurence of a line end
        pos = self.buffer.find(self.le)
        while pos > 0:
            #if a line end was found adda nything upt to it
            # as the first line to the line buffer
            self.lineBuffer.append(self.buffer[:pos])
            print("adding data to line buffer: %s" % repr(self.buffer[:pos]))
            #remove the data that was read as a line from the buffer
            #Note: if the line end is mutliple characters we want to skip them
            self.buffer = self.buffer[pos+len(self.le):] 
            #find the next line end
            pos = self.buffer.find(self.le)
        
        #check if the number of lines in the line buffer is as high as requested
        if len(self.lineBuffer) >= n:
            #reset line buffer
            tmp = self.lineBuffer
            self.lineBuffer = []
            print("returning: %s" % tmp)
            return tmp
        return None
    
    def readline(self):
        """Read one line from the serial port.
        
        Will raise an exception if no full line is available.
        """
        
        if self.port is None:
            raise TachyError("Not connected")
        if not self.port.canReadLine():
            raise ValueError("No full line is available")
        data = bytes(self.port.readLine()).decode("ascii")
        self.log.write("READ LINE: %s\n" % data)
        return data
    
    def read(self, size=1):
        """Read a certain number of bytes from the serial port."""
        
        if self.port is None:
            raise TachyError("Not connected")
        data = self.port.read(size).decode("ascii")
        self.log.write("READ: %s\n" % data)
        return data
        
    def write(self, data): 
        """Write Data to the serial port."""
        if self.port is None:
            raise TachyError("Not connected")
        d = bytes(data, "latin-1")
        self.log.write("WRITE: %s\n" % d)
        self.port.write(d)
        self.port.flush()
        #wait until write is done
        if not self.port.waitForBytesWritten(self.writeTimeout*1000):
            raise Timeout("Timeout during write")

    def readMeasurement(self):
        """Read a complete measurment from the serial port.
        
        Returns a dictionary representing the measurment oor None if
        no data is available.
        """
        if self.port is None:
            raise TachyError("Not connected")
        #read two lines
        lines = self.readLines(2)
        #if no data was read return None
        if lines is None:
            return None
        #check for the star at the start of the first line    
        rawStr = lines[0].strip()
        mStr = rawStr[1:]
        if rawStr[0] != "*":
            raise TachyError("Unexpected character at start of measurement: '%s'" % rawStr[0])

        #split the first line into parts    
        data_point = {}
        if not mStr:
            return None
        words = mStr.split(" ")
        #for each part of the measurment
        for word in words:
            #the "index" identifies the datum that is encoded
            word_index = word[0:2]
            data_info = word[3:6]
            #the rest is the actual value
            data = word[6:]
            #if this is a datum that can be converted to a number
            if word_index in self.digits:
                #put it into the right palce in the dictonary and convert it to a float value with
                # the right number of decimal digits
                data_point[self.codes[word_index]] = float(data)/10**self.digits[word_index]
            else:
                #non numerical data is saved verbatim
                data_point[self.codes[word_index]] = data
        #check that the second line is a "w"
        secondLine = lines[1].strip() 
        if secondLine != "w":
            raise TachyError("Unexpected character at end of measurement: '%s'" % secondLine)
        #return aknowledgment to the tachy
        self.write("OK\r\n")
        return data_point


    
    def setPosition(self, x, y, z=None):
        """Set the position of the Tachymeter conencted to the serial port"""
        
        #for x coordinate
        #write the command to the serial port
        # them command consists of a identifier (84) and the number in a format without a decimal point
        self.write("PUT/84...0"+ "%0+17.d \r\n" % (x*10**self.digits["84"])) #easting -> x
        #wait for aknowledgment from the Tachymeter
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
        #repeat for y and possibly z
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
            
    def setAngle(self, alpha):
        """Set the Tachymeter angle."""
        
        #write the command to the serial port
        # them command consists of a identifier (21) and the number in a format without a decimal point
        self.write("PUT/21...2"+ "%0+17.d \r\n" % (alpha*10**self.digits["21"]))
        #wait for aknowledgment from the Tachymeter
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        if line.strip() != "?":
            raise TachyError("Unexpected answer from Tachy: %s" % repr(line))
            
    def getAngle(self):
        """Get the current angle from the Tachymeter."""
        
        #send the command for returning the current angle
        self.write("GET/M/WI21\r\n")
        #wait for the answer from the tachy
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        #decode the answer from the tachy
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getReflectorHeight(self):
        """Get the reflector height property of the Tachymeter."""
        
        #send the command for returning the reflector height
        self.write("GET/M/WI87\r\n")  
        #wait for answer from tachy
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        line = lines[0]
        #decode tachy answer
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]

    def getInstrumentHeight(self):
        """Get the instrument height property of the Tachymeter."""
        
        #send the command for returnning the instrument height
        self.write("GET/M/WI88\r\n")  
        #wait for answer from tachy
        lines = None
        while lines is None:
            self.port.waitForReadyRead(500)
            lines = self.readLines(1)
        #decode tachy answer
        line = lines[0]
        word_index = line[1:3]
        data = line[-17:]
        return float(data)/10**self.digits[word_index]
        
    def beep(self):
        """Make the Tachymeter beep."""
        
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
        """Set the first stationing point.
        
        Use this function only for the first point of a free stationing.
        p has to be the real coordiantes of the first stationing point. 
        The measurment has to be the measured position of the same point.
        If no measurment is given it will be read from the serila port 
        (this options is deprecated).
        """
        
        #set the position of the tachymeter to the abitrary position 0,0,0 
        # to make computations easier
        self.setPosition(0.0, 0.0)
        
        #save real position of the point
        self.stationPoint = [p]
        #if no measumrent is given, read it from the serial port
        if measurement is None:
            print("no measurment for point 1. Starting measurment.")
            oldTimeout = self.timeout
            self.timeout = timeout
            self.port.write_timout = timeout
            mes = self.readMeasurement()
        else:
            mes = measurement
        
        #compute (horizontal) distance from the station to the point from vertical angle and sloped distance
        #this is basic pytagoras
        self.stationPointDist = [numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"] ]
        #save vertical and horizontal angle
        self.stationPointHAngle = [gon2rad(mes["hzAngle"])]
        self.stationPointVAngle = [gon2rad(mes["vertAngle"])]
        #get the reflector height from the measurment or altenaitvely from the Tachymeter and save it
        try:
            self.stationPointReflectorH = [ mes["reflectorHeight"] ]
        except KeyError:
            self.stationPointReflectorH = [self.getReflectorHeight()]
        if measurement is None:
            self.port.write_timout = oldTimeout
            self.timeout = oldTimeout
        
    def stationPointN(self, p, measurement=None, timeout=60):
        """Add an additional stationing point.
        
        Use this function for any point but the first.
        p has to be the real coordiantes of the first stationing point. 
        The measurment has to be the measured position of the same point.
        If no measurment is given it will be read from the serila port 
        (this options is deprecated).
        """
        
        #save real position of the point
        self.stationPoint.append(p)
        #if no measumrent is given, read it from the serial port
        if measurement is None:
            oldTimeout = self.timeout
            self.timeout = timeout
            self.port.write_timout = timeout
            mes = self.readMeasurement()
        else:
            mes = measurement
        #compute (horizontal) distance from the station to the point from vertical angle and sloped distance
        #this is basic pytagoras
        self.stationPointDist.append(numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"])
        #save vertical and horizontal angle
        self.stationPointHAngle.append(gon2rad(mes["hzAngle"]))
        self.stationPointVAngle.append(gon2rad(mes["vertAngle"]))
        #get the reflector height from the measurment or altenaitvely from the Tachymeter and save it
        try:
            self.stationPointReflectorH.append(mes["reflectorHeight"])
        except KeyError:
            self.stationPointReflectorH.append(self.getReflectorHeight())
        if measurement is None:
            self.port.write_timout = oldTimeout
            self.timeout = oldTimeout

    def computeHorizontalPositionAndAngle(self):
        """Compute the horizontal position (x and y) and angle of the station.
        
        Fix point data has to be added before with stationPoint[1|N] functions.
        """
        
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
        """Compute station height.
        
        Fix point data has to be added before with stationPoint[1|N] functions.
        a is the index of the stationing point that should be used for the computation.
        """
        
        #get the height difference between the station and the stationing point.
        g = numpy.sin(numpy.pi/2 - self.stationPointVAngle[a]) * self.stationPointDist[a]

        self.log.write("Computed height difference: %f\n" % (g))
        #get z coordinate of the used staioning point
        Za = self.stationPoint[a][2]
        #compute station height based on before comuted values and the istrument and reflector height
        ZS = Za - g + self.stationPointReflectorH[a] - self.getInstrumentHeight()
        self.log.write("Comuted heights: %f\n" % (ZS))
        return ZS
        
    
    def computeStation(self, timeout=60):
        """Compute the station of the Tachymeter.
        
        Fix point data has to be added before with stationPoint[1|N] functions.
        """
        
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
        """Set the station of the Tachymeter.
        
        i.e. x,y,z coordinates and horizontal angle."""
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
