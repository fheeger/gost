import sys

import numpy
import serial

import bpy

def dist(x1,y1,x2,y2):
    return numpy.sqrt((x1-x2)**2+(y1-y2)**2)

def polar2kart(alpha_g, dist):
    gon2rad = 2*numpy.pi/400
    alpha_r = alpha_g * gon2rad
    y = dist * numpy.sin(alpha_r)
    x = dist * numpy.cos(alpha_r)
    return (x,y)
    
def t_winkel(x1,y1,x2,y2):
    return numpy.arctan((y1-y2)/(x1-x2))
    
def rot(winkel_quel, winkel_ziel):
    return winkel_ziel-winkel_quel
    
def translation(rot, p_qx, p_qy, p_zx, p_zy):
    m=1
    x0 = p_zx - m * numpy.cos(rot) * p_qx + m * numpy.sin(rot) * p_qy
    y0 = p_zy - m * numpy.sin(rot) * p_qx - m * numpy.cos(rot) * p_qy
    return x0, y0
    
def transformation(x, y, eps, x0, y0):
    m=1
    xz = x0 + m * numpy.cos(eps) * x - m * numpy.sin(eps) * y
    yz = y0 + m * numpy.sin(eps) * x + m * numpy.cos(eps) * y
    return (x,y)
    
    


    
        
    
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
              }

    def __init__(self, dev, baut=4800, log=sys.stderr):
        self.port = serial.Serial(dev, baut)
        self.log = log

    def __del__(self):
        self.port.close()
        
    def readline(self):
        data = self.port.readline().decode("ascii")
        self.log.write("READ LINE: %s\n" % data)
        return data
        
    def write(self, data):
        d = bytes(data, "ascii")
        self.log.write("WRITE: %s\n" % d)
        self.port.write(d)

    def readMeasurment(self):
        data_point = {}
        mStr = self.readline()[1:].strip()
        lines = mStr.split(" ")
        for line in lines:
            word_index = line[0:2]
            data_info = line[3:7]
#            sign = line[7]
            data = line[7:]
            if word_index in self.digits:
                data_point[self.codes[word_index]] = float(data)/10**self.digits[word_index]
            else:
                data_point[self.codes[word_index]] = data
        if self.readline().strip() != "w":
            raise TachyError()
        self.write("OK\r\n")
        return data_point
        
    def stationierung(self, A, B):
        #set tachy position to zero
        self.setPosition(0.0, 0.0)
        a = self.readMeasurment()
#        self.log.write("%s\n" % self.port.read())
        self.log.write("Point one read %f %f\n" % (a["targetEast"], a["targetNorth"]))
        self.setAngle(0.0)
        
        b = self.readMeasurment()
        self.log.write("Point two read %f %f\n" % (b["targetEast"], b["targetNorth"]))
        
        sfsa = a["slopeDist"]
        sfsb = b["slopeDist"]
        beta = b["hzAngle"]*2*numpy.pi/400
        self.log.write("Abstand zu A: %f, Abstand zu B: %f, Winkel zu B: %f(rad)\n" % (sfsa, sfsb, beta))

        xa = 0
        ya = sfsa
        xb = sfsb * numpy.sin(beta)
        yb = sfsb * numpy.cos(beta)

        self.log.write("Quellkoordinatensystem: a %f %f, b %f %f\n" % (xa,ya,xb,yb))

        Xa, Ya, Za = A
        Xb, Yb, Zb = B
        self.log.write("Zeilkoordinatensystem: A %f %f, B %f %f\n" % (Xa,Ya,Xb,Yb))


        sab = dist(xa,ya,xb,yb)
        tab = numpy.arctan((xa-xb)/(ya-yb))
        self.log.write("Winkel im QKS: %f\n" % tab)
        Tab = numpy.arctan((Xa-Xb)/(Ya-Yb))
        self.log.write("Winkel im ZKS: %f\n" % Tab)
        
        phi = Tab - tab
        self.log.write("Rotationswinkel: %f\n" % phi)

        Yfs = Ya - sfsa * numpy.cos(phi)
        Xfs = Xa - sfsa * numpy.sin(phi)
        
        #set tachy position
        self.setPosition(Xfs, Yfs)
        self.log.write("Position set to %f %f\n" % (Xfs, Yfs))
        #set tachy angel
        a = self.getAngle()
        self.log.write("Current Angle is %f\n" % a)
        self.setAngle(a+phi*400/(2*numpy.pi))
        self.log.write("Angle set to %f\n" % (a+phi))
        self.log.write("Station set successful.\n")
    
    def setPosition(self, x, y):
        self.write("PUT/84...0"+ "%0+17.d \r\n" % (x*10**self.digits["84"])) #easting -> x
        if self.readline().strip() != "?":
            raise TachyError()
        self.write("PUT/85...0"+ "%0+17.d \r\n" % (y*10**self.digits["85"])) #nrothing -> y
        if self.readline().strip() != "?":
            raise TachyError()
            
    def setAngle(self, alpha):
        self.write("PUT/21...2"+ "%0+17.d \r\n" % (alpha*10**self.digits["21"])) #nrothing -> y
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
    
#hp2 = (0.6, 0)
#hp3 = (0, 0.8)
#tachy = TachyConnection("/dev/ttyUSB0")
#tachy.beep()

bpy.types.Scene.tachy = TachyConnection("COM1")


class StationPoint1(bpy.types.Operator):
    bl_idname = "mesh.station_point1"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        context.scene.tachy.setPosition(0.0, 0.0)
        bpy.types.Scene.stationPoint1 = bpy.context.scene.objects.active.location
        mes = context.scene.tachy.readMeasurment()
        context.scene.tachy.setAngle(0.0)
        bpy.types.Scene.distStationPoint1 = numpy.cos(mes["vertAngle"])/ mes["slopeDist"]
        return {"FINISHED"}

class StationPoint2(bpy.types.Operator):
    bl_idname = "mesh.station_point2"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        bpy.types.Scene.stationPoint2 = bpy.context.scene.objects.active.location
        mes = context.scene.tachy.readMeasurment()
        bpy.types.Scene.distStationPoint2 = numpy.cos(mes["vertAngle"])/ mes["slopeDist"]
        bpy.types.Scene.angleStationPoint2 = mes["hzAngle"]
        return {"FINISHED"}

class SetStation(bpy.types.Operator):
    bl_idname = "mesh.set_station"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        sfsa = context.scene.distStationPoint1
        sfsb = context.scene.distStationPoint2
        beta = context.scene.angleStationPoint2*2*numpy.pi/400
        #self.log.write("Abstand zu A: %f, Abstand zu B: %f, Winkel zu B: %f(rad)\n" % (sfsa, sfsb, beta))

        xa = 0
        ya = sfsa
        xb = sfsb * numpy.sin(beta)
        yb = sfsb * numpy.cos(beta)

        #self.log.write("Quellkoordinatensystem: a %f %f, b %f %f\n" % (xa,ya,xb,yb))

        Xa, Ya, Za = context.scene.stationPoint1
        Xb, Yb, Zb = context.scene.stationPoint2
        #self.log.write("Zeilkoordinatensystem: A %f %f, B %f %f\n" % (Xa,Ya,Xb,Yb))


        sab = dist(xa,ya,xb,yb)
        tab = numpy.arctan((xa-xb)/(ya-yb))
        #self.log.write("Winkel im QKS: %f\n" % tab)
        Tab = numpy.arctan((Xa-Xb)/(Ya-Yb))
        #self.log.write("Winkel im ZKS: %f\n" % Tab)
        
        phi = Tab - tab
        #self.log.write("Rotationswinkel: %f\n" % phi)

        Yfs = Ya - sfsa * numpy.cos(phi)
        Xfs = Xa - sfsa * numpy.sin(phi)
        
        #set tachy position
        context.scene.tachy.setPosition(Xfs, Yfs)
        #self.log.write("Position set to %f %f\n" % (Xfs, Yfs))
        #set tachy angel
        a = context.scene.tachy.getAngle()
        #self.log.write("Current Angle is %f\n" % a)
        context.scene.tachy.setAngle(a+phi*400/(2*numpy.pi))
        #self.log.write("Angle set to %f\n" % (a+phi))
        #self.log.write("Station set successful.\n")   
        return {"FINISHED"}



class MeasurePoint(bpy.types.Operator):
    bl_idname = "mesh.measure_point"
    bl_label = "Measure Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        measurment = context.scene.tachy.readMeasurment()
        print(measurment)
        x = measurment["targetEast"]
        y = measurment["targetNorth"]
        z = measurment["targetHeight"] 
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.context.scene.cursor_location = (x, y, z)
        bpy.context.area.type='VIEW_3D'
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        #bpy.context.area.type='TEXT_EDITOR'
        return {"FINISHED"}



class MeasureNiv(bpy.types.Operator):
    bl_idname = "mesh.measure_point"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        measurment = context.scene.tachy.readMeasurment()
        print(measurment)
        x = measurment["targetEast"]
        y = measurment["targetNorth"]
        z = measurment["targetHeight"] 
        
        value1 = bpy.context.scene.CountNiv
        bpy.context.scene.CountNiv += 1
        string1 = bpy.context.scene.NivString
        strval = str(string1)+str(value1)
        bpy.ops.object.text_add()
        ob = bpy.context.object
        ob.name = (str(strval))
        tcu = ob.data
        tcu.name = (str(strval))
        tcu.body = (str(strval))
        tcu.font = bpy.data.fonts[0]
        tcu.offset_x = -0.01
        tcu.offset_y = 0.03
        tcu.shear = 0
        tcu.size = .06
        tcu.space_character = 1.1
        tcu.space_word = 2
        tcu.extrude = 0.002
        tcu.fill_mode="FRONT"
        tcu.use_fill_deform = True
        tcu.fill_mode="FRONT"

       
        coords = [[x, y, z], [x-0.016, y+0.024, z], [x+0.016, y+0.024, z]]
        faces = [[0,2,1]]
        me = bpy.data.meshes.new("Triangle")
        ob = bpy.data.objects.new("Triangle", me)
        #bpy.context.scene.objects.link(ob)
        ob.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.link(ob)
        #mesh.from_pydata([context.scene.cursor_location], [], [])
        me.from_pydata(coords, [], faces)
        me.update()
        bpy.context.scene.objects.active = ob
        
        return {"FINISHED"}



class MeasureCheckpoint(bpy.types.Operator):
    bl_idname = "mesh.measure_checkpoint"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        measurment = context.scene.tachy.readMeasurment()
        print(measurment)
        x = measurment["targetEast"]
        y = measurment["targetNorth"]
        z = measurment["targetHeight"] 
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.context.scene.cursor_location = (x, y, z)
        bpy.context.area.type='VIEW_3D'
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        #bpy.context.area.type='TEXT_EDITOR'
        return {"FINISHED"}



class MeasurePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Tools"
    bl_label = "Measure Panel"
 
    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator("mesh.measure_point", text="Measure Point")
        
      
        
class TachyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"
    bl_label = "Tachy Panel"
     
   

 
    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator("mesh.station_point1", text="Station Point 1")
        layout.operator("mesh.station_point2", text="Station Point 2")
        layout = self.layout.column(align=True)
        layout.operator("mesh.set_station", text="Compute Station")
        


                

bpy.utils.register_module(__name__)