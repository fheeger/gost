bl_info = {
    "name": "GeO Survey Tool",
    "author": "Lukas Fischer, Felix Heeger",
    "blender": (2, 70, 0),
    "location": "",
    "description": "Connect to a Tachymeter and recieve data from it.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}
    

import sys
from glob import glob
import serial

import numpy
import bpy
import bmesh

from .tachy import TachyConnection, TachyError
from .util import dist, gon2rad, rad2gon


#class TachyConnect(bpy.types.Operator):
#    bl_idname = "tachy.connect"
#    bl_label = "Connect to Tachymeter"
#    
#    def invoke(self, context, event):
#        return context.window_manager.invoke_props_dialog(self, width=200, height=100)

#    def draw(self, context):
#        scn = bpy.context.scene
#        self.layout.prop_menu_enum(scn, "serialPorts")
#        
#    def execute(self, context):
#        return {"FINISHED"}

#class TACHY_OT_connect(bpy.types.Operator):
#    bl_idname = "tachy.create"
#    bl_label = "connect_tachymeter"
#    
#    def execute(self, context):
#        port = context.scene.serialPorts
#        print("Selected port:", port)
#        context.scene["tachy"] = TachyConnection(port)
#        return {"FINISHED"}

bpy.types.Scene.tachy = TachyConnection()

class SelectPortOperator(bpy.types.Operator):
    bl_idname = "tachy.select_port"
    bl_label = "Select serial port to connect Tachymeter"
    
    @classmethod
    def poll(cls, context):
        return not bpy.types.Scene.tachy.connected
    
    def avail_ports(self, context):
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
        names = ports + ["/dev/pts/15"]
        ids = ["p%i" % i for i in range(len(names))] 
        descriptions = names
        return list(zip(ids, names, descriptions))
        
    ports = bpy.props.EnumProperty(items=avail_ports, name="Ports")
    
    def execute(self, context):
        for i, port, _ in self.avail_ports(context):
            if i == self.ports:
                bpy.types.Scene.tachy.open(port)
                break
        return {"FINISHED"}

class StationPoint1(bpy.types.Operator):
    bl_idname = "tachy.station_point1"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.types.Scene.tachy.connected
    
    def invoke(self, context, event):
        return self.execute(context)
        
    def execute(self, context):
        context.scene.tachy.setPosition(0.0, 0.0)
        bpy.context.scene["stationPoint1"] = bpy.context.scene.objects.active.location
        mes = context.scene.tachy.readMeasurment()
        print(mes)
        context.scene.tachy.setAngle(0.0)
        bpy.context.scene["distStationPoint1"] = numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"]
        bpy.context.scene["vertAngleStationPoint1"] = gon2rad(mes["vertAngle"])
        bpy.context.scene["reflectorHeightStationPoint1"] = mes["reflectorHeight"]
        return {"FINISHED"}

class StationPoint2(bpy.types.Operator):
    bl_idname = "tachy.station_point2"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.types.Scene.tachy.connected
    
    def invoke(self, context, event):
        bpy.context.scene["stationPoint2"] = bpy.context.scene.objects.active.location
        mes = context.scene.tachy.readMeasurment()
        print(mes)
        bpy.context.scene["distStationPoint2"] = numpy.cos(gon2rad(mes["vertAngle"]) - numpy.pi/2)*mes["slopeDist"]
        bpy.context.scene["angleStationPoint2"] = mes["hzAngle"]
        bpy.context.scene["vertAngleStationPoint2"] = gon2rad(mes["vertAngle"])
        bpy.context.scene["reflectorHeightStationPoint2"] = mes["reflectorHeight"]
        return {"FINISHED"}

class SetStation(bpy.types.Operator):
    bl_idname = "tachy.set_station"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.types.Scene.tachy.connected and "stationPoint1" in bpy.context.scene and "stationPoint2" in bpy.context.scene
    
    def invoke(self, context, event):
        sA = context.scene["distStationPoint1"]
        sB = context.scene["distStationPoint2"]
        gamma = gon2rad(context.scene["angleStationPoint2"])
        print("Abstand zu A: %f, Abstand zu B: %f, Winkel zu B: %f(rad), %f(gon)\n" % (sA, sB, gamma, rad2gon(gamma)))

        #xa = 0
        #ya = sfsa
        #xb = sfsb * numpy.sin(beta)
        #yb = sfsb * numpy.cos(beta)

        #print("Quellkoordinatensystem: a %f %f, b %f %f\n" % (xa,ya,xb,yb))

        Ya, Xa, Za = context.scene["stationPoint1"]
        Yb, Xb, Zb = context.scene["stationPoint2"]
        print("Zeilkoordinatensystem: A %f %f, B %f %f\n" % (Xa,Ya,Xb,Yb))


        #sab = dist(xa,ya,xb,yb)
        SAB = dist(Xa, Ya, Xb, Yb) 
        print("Abstand zwischen A und B:%f" % SAB)
        #tab = numpy.arctan((xb - xa)/(yb - ya))
        #print("Winkel im QKS: %f(rad), %f(gon)\n" % (tab, tab * 400/(2*numpy.pi)))
        tAB = numpy.arctan((Yb - Ya)/(Xb - Xa)) % (2*numpy.pi)
        print("Winkel im ZKS: %f(rad), %f(gon)\n" % (tAB, rad2gon(tAB)))
        
        #phi = Tab - tab
        print("arccos((%f**2+%f**2-%f**2)/(2*%f*%f))" % (sA,SAB,sB,sA,SAB))
        print("=arccos(%f)" % ((sA**2+SAB**2-sB**2)/(2*sA*SAB)))
        alpha = numpy.arccos(min(1, (sA**2+SAB**2-sB**2)/(2*sA*SAB)))
        print("Alpha: %f(rad), %f(gon)" % (alpha, rad2gon(alpha)))
        tAS = tAB + alpha
        print("Rotationswinkel: %f(rad), %f(gon)\n" % (tAS, rad2gon(tAS)))

        #wenn der x wer des zweiten punkts kleiner ist als der des ersten muss man subtrahieren
        if Xb < Xa:
            XS = Xa - sA * numpy.cos(tAS)
            YS = Ya - sA * numpy.sin(tAS)
        else:
            XS = Xa + sA * numpy.cos(tAS)
            YS = Ya + sA * numpy.sin(tAS)
        
        Ga = numpy.sin(bpy.context.scene["vertAngleStationPoint1"] - numpy.pi/2) * bpy.context.scene["distStationPoint1"]
        Gb = numpy.sin(bpy.context.scene["vertAngleStationPoint2"] - numpy.pi/2) * bpy.context.scene["distStationPoint2"]

        print("Computed height difference: %f, %f" % (Ga, Gb))
        
        ZS_list = [Za - Ga + bpy.context.scene["reflectorHeightStationPoint1"],
                   Zb - Gb + bpy.context.scene["reflectorHeightStationPoint2"]]
        print("Comuted heights: %f, %f" % tuple(ZS_list))
        ZS = numpy.mean(ZS_list)
        
        #set tachy position
        context.scene.tachy.setPosition(YS, XS, ZS)
        bpy.context.scene["tachyPosition"] = (YS, XS, ZS)
        print("Position set to %f %f %f\n" % (YS, XS, ZS))
        #set tachy angel
        a = context.scene.tachy.getAngle()
        print("Current Angle is %f\n" % a)
        context.scene.tachy.setAngle(a+rad2gon(tAS))
        print("Angle set to %f\n" % (a+rad2gon(tAS)))
        print("Station set successful.\n")   
        return {"FINISHED"}



class MeasurePoints(bpy.types.Operator):
    bl_idname = "tachy.measure_points"
    bl_label = "Measure Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        if not bpy.types.Scene.tachy.connected:
            return False
        if not "tachyPosition" in bpy.context.scene:
            return False
        num_selected_vert = 0
        
        for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts :
            if v.select:
                num_selected_vert += 1
        if num_selected_vert != 1:
            return False
        return True
    
    def invoke(self, context, event):
        print("start measurment")
        print(context.window_manager.modal_handler_add(self))
        self._timer = context.window_manager.event_timer_add(1, context.window)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == "ESC":
            print("stopping measurment")
            context.window_manager.event_timer_remove(self._timer)
            return {"FINISHED"}
        elif event.type == "TIMER":
            return self.execute(context)
        return {"PASS_THROUGH"}
    
    def execute(self, context):
        try:
            measurment = context.scene.tachy.readMeasurementNonBlocking(0.1)
            if measurment is None:
                print("No measurment")
                return {"RUNNING_MODAL"}
            else:
                print(measurment)
                x = measurment["targetEast"]
                y = measurment["targetNorth"]
                z = measurment["targetHeight"] 
                bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                bpy.context.scene.cursor_location = (x, y, z)
                bpy.context.area.type='VIEW_3D'
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                #bpy.context.area.type='TEXT_EDITOR'
                return {"RUNNING_MODAL"}
        except TachyError:
            self.report({"ERROR"}, "Error in tachy communication")


class MeasureNiv(bpy.types.Operator):
    bl_idname = "tachy.measure_niv"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        measurment = context.scene.tachy.readMeasurment()
        print(measurment)
        x = measurment["targetEast"]
        y = measurment["targetNorth"]
        z = measurment["targetHeight"] 
        
        bpy.context.scene.cursor_location = (x, y, z)
        
        strval = "%.2f m NN" % z
        bpy.ops.object.text_add()
        ob = bpy.context.object
        ob.name = (strval)
        tcu = ob.data
        tcu.name = (strval)
        tcu.body = (strval)
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

       
        coords = [[0, 0, 0], [-0.016, 0.024, 0], [0.016, 0.024, 0]]
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
    bl_idname = "tachy.measure_checkpoint"
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
        layout.operator("tachy.measure_points", text="Measure Points")
        


class TachyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"
    bl_label = "Tachy Panel"

    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator_menu_enum("tachy.select_port", property="ports", text="Connect Tachymeter")
        layout = self.layout.column(align=True)
        layout.operator("tachy.station_point1", text="Station Point 1")
        layout.operator("tachy.station_point2", text="Station Point 2")
        layout = self.layout.column(align=True)
        layout.operator("tachy.set_station", text="Compute Station")
        layout = self.layout.column(align=True)
        layout.operator("tachy.measure_niv", text="Measure Nivellemnet")
        


                
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)