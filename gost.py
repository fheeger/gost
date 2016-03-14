#Copyright (C) 2015 - 2016 Felix Heeger
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
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from .tachy import TachyConnection

class QtGostApp(QWidget):
    def __init__(self, parent=None):
        super(QtGostApp, self).__init__(parent)
        
        self.connectButton = QPushButton("Mit Tachymeter verbinden")
        self.stationButton = QPushButton("Freie Stationierung")
        self.stationButton.setEnabled(False)
        
        mainLayout = QBoxLayout(2)
        mainLayout.addWidget(self.connectButton)
        mainLayout.addWidget(self.stationButton)
        self.setLayout(mainLayout)
        
        self.connectButton.clicked.connect(self.openConnectWindow)
        self.stationButton.clicked.connect(self.openStationWindow)
        
        self.connection = TachyConnection()
        
        self.setWindowTitle("GeO Survey Tool - GOST")
        
    def openConnectWindow(self):
        connectWindow = QtGostConnect(self)
        connectWindow.show()
    
    def openStationWindow(self):
        stationWindow = QtGostStation(self)
        stationWindow.show()
    
    def closeEvent(self, event):
        if self.connection.connected:
            print("closing tachy connection")
            self.connection.close()
        event.accept()

class QtGostConnect(QDialog):
    posBautRates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    
    def __init__(self, parent=None):
        super(QtGostConnect, self).__init__(parent)
        
        self.selectPort = QComboBox(self)
        for port in self.avail_ports():
            self.selectPort.addItem(port)
        self.selectBautRate = QComboBox(self)
        self.selectBautRate.addItems([str(b) for b in self.posBautRates])
        self.selectBautRate.setCurrentIndex(11)
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        
                
        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel("COM port:"), 0, 0)
        mainLayout.addWidget(self.selectPort, 0, 1)
        mainLayout.addWidget(QLabel("Baut rate:"),1, 0)
        mainLayout.addWidget(self.selectBautRate, 1, 1)
        mainLayout.addWidget(self.okButton, 2, 0)
        mainLayout.addWidget(self.cancleButton, 2, 1)
        self.setLayout(mainLayout)
 
        self.okButton.clicked.connect(self.accept) 
        self.cancleButton.clicked.connect(self.reject)

    def avail_ports(self):
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
        # uncommend this line with the according path for pseudo ports in linux
        #ports.append("/dev/pts/18")
        return ports

    def accept(self):
        port = self.selectPort.currentText()
        bautrate = int(self.selectBautRate.currentText())
        print("connecting to port: %s, with baut rate %i" % (port, bautrate))
        self.parentWidget().connection.open(port, bautrate)
        self.parentWidget().connectButton.setEnabled(False)
        self.parentWidget().stationButton.setEnabled(True)
        # self.meassureButton.setEnabled(True)
        super(QtGostConnect, self).accept()
    
class QtGostStation(QDialog):
    def __init__(self, parent=None):
        super(QtGostStation, self).__init__(parent)
        
        self.pointList = QListView()
        self.pointModel = QStandardItemModel(self.pointList)
        self.xLab = QLabel("NA")
        self.yLab = QLabel("NA")
        self.zLab = QLabel("NA")
        self.errorLab = QLabel("NA")
        self.computeButton = QPushButton("Station Berechnen")
        self.okButton = QPushButton("Ok")
        self.cancleButton = QPushButton("Abbrechen")
        
        mainLayout = QBoxLayout(2)
        mainLayout.addWidget(QLabel("Derzeitige Stationierung:"))
        
        stationLayout = QBoxLayout(0)
        stationLayout.addWidget(QLabel("x:"))
        stationLayout.addWidget(self.xLab)
        stationLayout.addWidget(QLabel("y:"))
        stationLayout.addWidget(self.yLab)
        stationLayout.addWidget(QLabel("z:"))
        stationLayout.addWidget(self.zLab)
        stationLayout.addWidget(QLabel("std. Fehler:"))
        stationLayout.addWidget(self.errorLab)
        
        mainLayout.addLayout(stationLayout)
        mainLayout.addWidget(self.pointList)
        
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.okButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.cancleButton, QDialogButtonBox.RejectRole)
        buttonBox.addButton(self.computeButton, QDialogButtonBox.ApplyRole)
        
        mainLayout.addWidget(buttonBox)
        
        self.setLayout(mainLayout)
    
# class QtNivel(QDialog):
    # def __init__(self, parent=None):
        # super(QtNivel, self).__init__(parent)
        

        
        # self.xField = QLineEdit()
        # self.yField = QLineEdit()
        # self.zField = QLineEdit()
        
        # mainLayout = QGridLayout()
        # mainLayout.addWidget(QLabel("x:"), 0, 0)
        # mainLayout.addWidget(self.xField , 0, 1)
        # mainLayout.addWidget(QLabel("y:"), 1, 0)
        # mainLayout.addWidget(self.yField, 1, 1)
        # mainLayout.addWidget(QLabel("z:"), 2, 0)
        # mainLayout.addWidget(self.zField, 2, 1)
        
        # button = QPushButton('Add Nivelement', self)
        # mainLayout.addWidget(button, 3, 0)
        
        # self.setLayout(mainLayout)
        
        # button.clicked.connect(self.addNivel)
        
    # def addNivel(self, *args):
          
        # global context
            
        # x = float(self.xField.text()) 
        # y = float(self.yField.text())
        # z = float(self.zField.text())
        
        # print("creating niv at %f,%f,%f" % (x,y,z))
        
        # #context["scene"].cursor_location = (x, y, z)
        # bpy.context.scene.cursor_location = (x, y, z)
        
        # strval = "%.2f m NN" % z
        # bpy.ops.object.text_add()
        # ob = bpy.data.objects["Text"]
        # print(str(ob))
        # ob.name = (strval)
        # tcu = ob.data
        # tcu.name = (strval)
        # tcu.body = (strval)
        # tcu.font = bpy.data.fonts[0]
        # tcu.offset_x = -0.01
        # tcu.offset_y = 0.03
        # tcu.shear = 0
        # tcu.size = .06
        # tcu.space_character = 1.1
        # tcu.space_word = 2
        # tcu.extrude = 0.002
        # tcu.fill_mode="FRONT"
        # tcu.use_fill_deform = True
        # tcu.fill_mode="FRONT"

       
        # coords = [[0, 0, 0], [-0.016, 0.024, 0], [0.016, 0.024, 0]]
        # faces = [[0,2,1]]
        
        # me = bpy.data.meshes.new("Triangle")
        # tr = bpy.data.objects.new("Triangle", me)
        # #bpy.context.scene.objects.link(ob)
        # tr.location = context["scene"].cursor_location
        # context["scene"].objects.link(tr)
        # #mesh.from_pydata([context.scene.cursor_location], [], [])
        # me.from_pydata(coords, [], faces)
        # me.update()
        # context["scene"].objects.active = ob
        
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

# bpy.types.Scene.tachy = TachyConnection()

# class SelectPortOperator(bpy.types.Operator):
    # bl_idname = "tachy.select_port"
    # bl_label = "Select serial port to connect Tachymeter"
    
    # @classmethod
    # def poll(cls, context):
        # return not bpy.types.Scene.tachy.connected
    
    # def avail_ports(self, context):
        # if sys.platform[:3] == "win":
            # possible = ["COM%i" % i for i in range(1,255)]
        # else:
            # possible = glob("/dev/tty[a-zA-Z]*")
        # ports = []
        # for p in possible:
            # try:
                # serial.Serial(p).close()
            # except serial.SerialException:
                # pass
            # else:
                # ports.append(p)
        # names = ports + ["/dev/pts/5"]
        # ids = ["p%i" % i for i in range(len(names))] 
        # descriptions = names
        # return list(zip(ids, names, descriptions))
        
    # ports = bpy.props.EnumProperty(items=avail_ports, name="Ports")
    
    # def execute(self, context):
        # for i, port, _ in self.avail_ports(context):
            # if i == self.ports:
                # bpy.types.Scene.tachy.open(port)
                # break
        # return {"FINISHED"}

# class StationPoint1(bpy.types.Operator):
    # bl_idname = "tachy.station_point1"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected
    
    # def invoke(self, context, event):
        # return self.execute(context)
        
    # def execute(self, context):
        # context.scene.tachy.stationPoint1(bpy.context.scene.objects.active.location)
        # return {"FINISHED"}

# class AddStationPoint(bpy.types.Operator):
    # bl_idname = "tachy.add_station_point"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected \
               # and len(context.scene.tachy.stationPoint) > 0
    
    # def invoke(self, context, event):
        # context.scene.tachy.stationPointN(bpy.context.scene.objects.active.location)
        # return {"FINISHED"}



# class SetStation(bpy.types.Operator):
    # bl_idname = "tachy.set_station"
    # bl_label = "Set Station"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # return bpy.types.Scene.tachy.connected \
               # and len(context.scene.tachy.stationPoint) > 2

    # #def getStationPoints(self, context):
    # #    pos, errors = bpy.types.Scene.tachy.computeStation()
    # #    retv = list(zip(["sPoint%i" % i for i in range(len(errors))], 
    # #                    ["(%f, %f, %f); error: %f" % (p[0],p[1],p[2],e) for p,e in zip(bpy.types.Scene.tachy.stationPoint[1:],errors)], 
    # #                    ["" % e for e in errors])
    # #                )
    # #    print(retv)
    # #    return retv

    # #sPointEnum = bpy.props.EnumProperty(items=getStationPoints, name="StaionPoints")

    # def invoke(self, context, event):
        # pos, angle = bpy.types.Scene.tachy.computeStation()
        # bpy.types.Scene.tachy.setStation(pos, angle)
        # return {"FINISHED"}



# class MeasurePoints(bpy.types.Operator):
    # bl_idname = "tachy.measure_points"
    # bl_label = "Measure Panel"
    # bl_options = {"UNDO"}
    
    # @classmethod
    # def poll(cls, context):
        # if not bpy.types.Scene.tachy.connected:
            # return False
        # if not bpy.types.Scene.tachy.stationed:
            # return False

# #        num_selected_vert = 0
# #        for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts :
# #            if v.select:
# #                num_selected_vert += 1
# #        if num_selected_vert != 1:
# #            return False
        # return True
    
    # def invoke(self, context, event):
        # print("start measurement")
        # print(context.window_manager.modal_handler_add(self))
        # self._timer = context.window_manager.event_timer_add(3, context.window)
        
        # return {'RUNNING_MODAL'}
    
    # def modal(self, context, event):
        # if event.type == "ESC":
            # print("stopping measurement")
            # context.window_manager.event_timer_remove(self._timer)
            # return {"FINISHED"}
        # elif event.type == "S" or event.type == "C":
            # #close
            # print("close line")
            # self.close_line()
            # return {"RUNNING_MODAL"}
        # elif event.type == "U" or event.type == "B":
            # #break
            # print("break line")
            # self.break_line()
            # return {"RUNNING_MODAL"}
        # elif event.type == "TIMER":
            # return self.execute(context)
        # return {"PASS_THROUGH"}
    
    # def execute(self, context):
        # try:
            # measurement = context.scene.tachy.readMeasurement(0.1)
            # if measurement is None:
                # print("No measurement")
                # return {"RUNNING_MODAL"}
            # else:
                # print(measurement)
                # x = measurement["targetEast"]
                # y = measurement["targetNorth"]
                # z = measurement["targetHeight"] 
                # bpy.context.area.type='VIEW_3D'
                # if len(bpy.context.selected_objects) == 0:
                    # print("No object selected")
                    # if bpy.context.mode != "OBJECT":
                        # bpy.ops.object.mode_set(mode='OBJECT')
                    # bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(x, y, z))
                    # bpy.ops.object.mode_set(mode='EDIT')
                    # bpy.ops.mesh.delete(type="VERT")
                    # bpy.ops.object.mode_set(mode='OBJECT')
                    # mesh = bpy.context.active_object
                    # mesh.data.vertices.add(1)
                    # mesh.data.vertices[0].co = (0, 0, 0)
                # else:
                    
                    # bpy.ops.object.mode_set(mode='EDIT')
                    # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                    # bpy.context.scene.cursor_location = (x, y, z)
                    # bpy.context.area.type='VIEW_3D'
                    # bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                    # #bpy.context.area.type='TEXT_EDITOR'
                # return {"RUNNING_MODAL"}
        # except TachyError:
            # self.report({"ERROR"}, "Error in tachy communication")

    # def close_line(self):
        # if bpy.context.mode != "EDIT":
                # bpy.ops.object.mode_set(mode='EDIT')
        # b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        # #unselect all vertices
        # for v in b.verts:
            # v.select = False
        # #select first and last vertex
        # b.verts.ensure_lookup_table()
        # b.verts[0].select = True
        # b.verts[-1].select = True
        # #add edge between them
        # bpy.ops.mesh.edge_face_add()
        # #mark edeges for freestyle render (select all edges first)
        # for e in b.edges:
            # e.select=True
        # bpy.ops.mesh.mark_freestyle_edge(clear=False)
        # #fill
        # bpy.ops.mesh.fill()
        # #recalculate normals
        # bpy.ops.mesh.normals_make_consistent()
        # bpy.ops.object.mode_set(mode='OBJECT')
        # #make shading smooth
        # bpy.ops.object.shade_smooth()
        # #unselect the object so the next measurment starts a new mesh
        # bpy.context.object.select = False
        
    # def break_line(self):
        # b = bmesh.from_edit_mesh(bpy.context.active_object.data)
        # #unselect all vertices
        # for v in b.verts:
            # v.select = False
        # #select first and last vertex
        # b.verts[0].select = True
        # b.verts[-1].select = True
        # #add edge between them
        # bpy.ops.mesh.edge_face_add()
        # b.verts[0].select = False
        # b.verts[-1].select = False

# class MeasureNiv(bpy.types.Operator):
    # bl_idname = "tachy.measure_niv"
    # bl_label = "Tachy Panel"
    # bl_options = {"UNDO"}
    
    # def invoke(self, context, event):
        # measurement = context.scene.tachy.readMeasurement()
        # print(measurement)
        # x = measurement["targetEast"]
        # y = measurement["targetNorth"]
        # z = measurement["targetHeight"] 
        
        # bpy.context.scene.cursor_location = (x, y, z)
        
        # strval = "%.2f m NN" % z
        # bpy.ops.object.text_add()
        # ob = bpy.context.object
        # ob.name = (strval)
        # tcu = ob.data
        # tcu.name = (strval)
        # tcu.body = (strval)
        # tcu.font = bpy.data.fonts[0]
        # tcu.offset_x = -0.01
        # tcu.offset_y = 0.03
        # tcu.shear = 0
        # tcu.size = .06
        # tcu.space_character = 1.1
        # tcu.space_word = 2
        # tcu.extrude = 0.002
        # tcu.fill_mode="FRONT"
        # tcu.use_fill_deform = True
        # tcu.fill_mode="FRONT"

       
        # coords = [[0, 0, 0], [-0.016, 0.024, 0], [0.016, 0.024, 0]]
        # faces = [[0,2,1]]
        
        # me = bpy.data.meshes.new("Triangle")
        # ob = bpy.data.objects.new("Triangle", me)
        # #bpy.context.scene.objects.link(ob)
        # ob.location = bpy.context.scene.cursor_location
        # bpy.context.scene.objects.link(ob)
        # #mesh.from_pydata([context.scene.cursor_location], [], [])
        # me.from_pydata(coords, [], faces)
        # me.update()
        # bpy.context.scene.objects.active = ob
        
        # return {"FINISHED"}



# # class MeasureCheckpoint(bpy.types.Operator):
    # # bl_idname = "tachy.measure_checkpoint"
    # # bl_label = "Tachy Panel"
    # # bl_options = {"UNDO"}
    
    # # def invoke(self, context, event):
        # # measurement = context.scene.tachy.readMeasurement()
        # # print(measurement)
        # # x = measurement["targetEast"]
        # # y = measurement["targetNorth"]
        # # z = measurement["targetHeight"] 
        # # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        # # bpy.context.scene.cursor_location = (x, y, z)
        # # bpy.context.area.type='VIEW_3D'
        # # bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        # bpy.context.area.type='TEXT_EDITOR'
        # # return {"FINISHED"}



# class MeasurePanel(bpy.types.Panel):
    # bl_space_type = "VIEW_3D"
    # bl_region_type = "TOOLS"
    # bl_context = "mesh_edit"
    # bl_category = "Tools"
    # bl_label = "Measure Panel"

    # def draw(self, context):
        # layout = self.layout.column(align=True)
        # layout.operator("tachy.measure_points", text="Measure Points")
        
