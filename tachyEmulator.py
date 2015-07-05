import sys

import serial

class Tachy:
    def __init__(self, dev, baut=4800, log=sys.stderr):
        self.port = serial.Serial(dev, baut)
        self.log = log
        
        self.angle = 100.0
        self.x = 3.5
        self.y = 1.4
    
    def readline(self):
        line = self.port.readline()
        self.log.write("READ LINE: %s" % line)
        return line
        
    def write(self, data):
        self.log.write("WRITE: %s" % data)
        self.port.write(data)
        
    def read(self, bytes=1, timeout=None):
        if not timeout is None:
            self.port.timeout = timeout
        data = self.port.read(bytes)
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
                self.write("*21.322%0+17.d\r\n" % self.angle)
            else:
                self.write("@W127\r\n")
        elif comArr[0] == "PUT":
            if comArr[1][:2] == "21":
                self.angle = float(comArr[1][-17:]) / 10**5
                self.write("?\r\n")
            elif comArr[1][:2] == "84":
                self.x = float(comArr[1][-17:]) / 10**3
                self.write("?\r\n")
            elif comArr[1][:2] == "85":
                self.y = float(comArr[1][-17:]) / 10**3
                self.write("?\r\n")
            else:
                self.write("@W127\r\n")
        else:
            self.write("@W127\r\n")
            