bl_info = {
    "name": "GOST: GeO Survey Tool",
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
        names = ports + ["/dev/pts/5"]
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
        context.scene.tachy.stationPoint1(bpy.context.scene.objects.active.location)
        return {"FINISHED"}

class AddStationPoint(bpy.types.Operator):
    bl_idname = "tachy.add_station_point"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.types.Scene.tachy.connected \
               and len(context.scene.tachy.stationPoint) > 0
    
    def invoke(self, context, event):
        context.scene.tachy.stationPointN(bpy.context.scene.objects.active.location)
        return {"FINISHED"}



class SetStation(bpy.types.Operator):
    bl_idname = "tachy.set_station"
    bl_label = "Set Station"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        return bpy.types.Scene.tachy.connected \
               and len(context.scene.tachy.stationPoint) > 2

    #def getStationPoints(self, context):
    #    pos, errors = bpy.types.Scene.tachy.computeStation()
    #    retv = list(zip(["sPoint%i" % i for i in range(len(errors))], 
    #                    ["(%f, %f, %f); error: %f" % (p[0],p[1],p[2],e) for p,e in zip(bpy.types.Scene.tachy.stationPoint[1:],errors)], 
    #                    ["" % e for e in errors])
    #                )
    #    print(retv)
    #    return retv

    #sPointEnum = bpy.props.EnumProperty(items=getStationPoints, name="StaionPoints")

    def invoke(self, context, event):
        pos, angle = bpy.types.Scene.tachy.computeStation()
        bpy.types.Scene.tachy.setStation(pos, angle)
        return {"FINISHED"}



class MeasurePoints(bpy.types.Operator):
    bl_idname = "tachy.measure_points"
    bl_label = "Measure Panel"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(cls, context):
        if not bpy.types.Scene.tachy.connected:
            return False
        if not bpy.types.Scene.tachy.stationed:
            return False

#        num_selected_vert = 0
#        for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts :
#            if v.select:
#                num_selected_vert += 1
#        if num_selected_vert != 1:
#            return False
        return True
    
    def invoke(self, context, event):
        print("start measurement")
        print(context.window_manager.modal_handler_add(self))
        self._timer = context.window_manager.event_timer_add(3, context.window)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == "ESC":
            print("stopping measurement")
            context.window_manager.event_timer_remove(self._timer)
            return {"FINISHED"}
        elif event.type == "S" or event.type == "C":
            #close
            print("close line")
            self.close_line()
            return {"RUNNING_MODAL"}
        elif event.type == "U" or event.type == "B":
            #break
            print("break line")
            self.break_line()
            return {"RUNNING_MODAL"}
        elif event.type == "TIMER":
            return self.execute(context)
        return {"PASS_THROUGH"}
    
    def execute(self, context):
        try:
            measurement = context.scene.tachy.readMeasurement(0.1)
            if measurement is None:
                print("No measurement")
                return {"RUNNING_MODAL"}
            else:
                print(measurement)
                x = measurement["targetEast"]
                y = measurement["targetNorth"]
                z = measurement["targetHeight"] 
                bpy.context.area.type='VIEW_3D'
                if len(bpy.context.selected_objects) == 0:
                    print("No object selected")
                    if bpy.context.mode != "OBJECT":
                        bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(x, y, z))
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.delete(type="VERT")
                    bpy.ops.object.mode_set(mode='OBJECT')
                    mesh = bpy.context.active_object
                    mesh.data.vertices.add(1)
                    mesh.data.vertices[0].co = (0, 0, 0)
                else:
                    
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                    bpy.context.scene.cursor_location = (x, y, z)
                    bpy.context.area.type='VIEW_3D'
                    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                    #bpy.context.area.type='TEXT_EDITOR'
                return {"RUNNING_MODAL"}
        except TachyError:
            self.report({"ERROR"}, "Error in tachy communication")

    def close_line(self):
        if bpy.context.mode != "EDIT":
                bpy.ops.object.mode_set(mode='EDIT')
        b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        #unselect all vertices
        for v in b.verts:
            v.select = False
        #select first and last vertex
        b.verts.ensure_lookup_table()
        b.verts[0].select = True
        b.verts[-1].select = True
        #add edge between them
        bpy.ops.mesh.edge_face_add()
        #mark edeges for freestyle render (select all edges first)
        for e in b.edges:
            e.select=True
        bpy.ops.mesh.mark_freestyle_edge(clear=False)
        #fill
        bpy.ops.mesh.fill()
        #recalculate normals
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.mode_set(mode='OBJECT')
        #make shading smooth
        bpy.ops.object.shade_smooth()
        #unselect the object so the next measurment starts a new mesh
        bpy.context.object.select = False
        
    def break_line(self):
        b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        #unselect all vertices
        for v in b.verts:
            v.select = False
        #select first and last vertex
        b.verts[0].select = True
        b.verts[-1].select = True
        #add edge between them
        bpy.ops.mesh.edge_face_add()
        b.verts[0].select = False
        b.verts[-1].select = False

class MeasureNiv(bpy.types.Operator):
    bl_idname = "tachy.measure_niv"
    bl_label = "Tachy Panel"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        measurement = context.scene.tachy.readMeasurement()
        print(measurement)
        x = measurement["targetEast"]
        y = measurement["targetNorth"]
        z = measurement["targetHeight"] 
        
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
        measurement = context.scene.tachy.readMeasurement()
        print(measurement)
        x = measurement["targetEast"]
        y = measurement["targetNorth"]
        z = measurement["targetHeight"] 
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
        layout.operator("tachy.add_station_point", text="Add Station Point")
        layout = self.layout.column(align=True)
        layout.operator("tachy.set_station", text="Compute Station")
        layout = self.layout.column(align=True)
        layout.operator("tachy.measure_niv", text="Measure Nivellemnet")
        layout.operator("tachy.measure_points", text="Measure Points")
        


                
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
