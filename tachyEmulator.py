#Copyright (C) 2015 Felix Heeger
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

import serial

class Tachy:
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

    def __init__(self, dev, baut=4800, log=sys.stderr):
        self.port = serial.Serial(dev, baut)
        self.log = log
        
        self.hzAngle = 100.0
        self.vertAngle = 0.0
        self.x = 3.5
        self.y = 1.4
        self.z = 1.0
        self.instrumentHeight=1.7
        
    
    def readline(self):
        line = self.port.readline().decode("ascii")
        self.log.write("READ LINE: %s" % line)
        return line
        
    def write(self, data):
        self.log.write("WRITE: %s" % data)
        self.port.write(bytes(data, "ascii"))
        
    def read(self, bytes=1, timeout=None):
        if not timeout is None:
            self.port.timeout = timeout
        data = self.port.read(bytes).decode("ascii")
        self.log.write("READ: %s\n" % data)
        return data
        
    def clear(self):
        char = "a"
        while char:
            char = self.read(1,0.1)
        
    def pointA(self):
        self.point("110005+0000000000000D12 21.322+0000000039819000 22.322+0000000009554300 31..00+0000000000004334 81..00-0000000000000123 82..00+0000000000004321 83..00+0000000000002326 87..10+0000000000001700")
        
    def pointB(self):
        self.point("110006+0000000000000D13 21.322+0000000001290800 22.322+0000000009579900 31..00+0000000000004697 81..00+0000000000000944 82..00+0000000000004591 83..00+0000000000002333 87..10+0000000000001700")
        
        
    def anyPoint(self, ptNr, x, y, z, hz, vert, dist, reflectorH=0):
        self.point("110006%+017.f 21.322%+017.f 22.322%+017.f 31..00%+017.f 81..00%+017.f 82..00%+017.f 83..00%+017.f 87..10%+017.f" % (ptNr, hz*10**5, vert*10**5, dist*10**3, x*10**3, y*10**3, z*10**3, reflectorH*10**3))
        
    def point(self, data):
        self.clear()
        self.write("*%s\r\n" % data)
        self.write("w\r\n")
        answer = self.read(2,1)
        if answer != "OK":
            self.log.write("Kommunikation Fehlgeschlagen\n")
        else:
            self.log.write("Messung erfolgreich\n")
            
    def wait(self):
        buffer = ""
        char = ""
        while char != "\r" or len(buffer.strip()) == 0 :
            char = self.read(1,99999)
            buffer += char
        self.readCommand(buffer)
        
    def readCommand(self, comStr):
        comArr = comStr.strip().split("/")
        print(comArr)
        if comArr[0] == "GET":
            if comArr[2] == "WI21":
                self.write("*21.322%0+17.d\r\n" % self.hzAngle)
            elif comArr[2] == "WI88":
                self.write("*88.322%0+17.d\r\n" % self.instrumentHeight)
            else:
                self.write("@W127\r\n")
        elif comArr[0] == "PUT":
            if comArr[1][:2] == "21":
                self.hzAngle = float(comArr[1][-17:]) / 10**5
                self.write("?\r\n")
            elif comArr[1][:2] == "84":
                self.x = float(comArr[1][-17:]) / 10**3
                self.write("?\r\n")
            elif comArr[1][:2] == "85":
                self.y = float(comArr[1][-17:]) / 10**3
                self.write("?\r\n")
            elif comArr[1][:2] == "86":
                self.z = float(comArr[1][-17:]) / 10**3
                self.write("?\r\n")
            else:
                self.write("@W127\r\n")
        else:
            self.write("@W127\r\n")
            
            
    def sPoint1(self):
        self.anyPoint(1,1,1,1,hz=0,vert=8.49,dist=22.56)

    def sPoint2(self):
        self.anyPoint(2,1,1,1,hz=40.96,vert=-14.004444,dist=22.91)
        
    def sPoint3(self):
        self.anyPoint(1,1,1,1,1,13.74,11.67)

    def sPoint4(self):
        self.anyPoint(1,1,1,1,123.87,8.92,17.9)
        
    def fstStPoint(self, dist, vert=100):
        self.wait()
        self.wait()
        self.anyPoint(1,1,1,1,1,vert=vert, dist=dist)
        self.stPointNr=1
        self.wait()
        
    def addStPoint(self, dist, angle, vert=100):
        self.stPointNr += 1
        self.anyPoint(self.stPointNr, 1, 1, 1, angle, vert=vert, dist=dist)
        
    def computeStation(self):
        for i in range(5):
            self.wait()

