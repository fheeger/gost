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
    

# import sys
# from glob import glob
# import serial

# import numpy
# import bpy
# import bmesh

# from .tachy import TachyConnection, TachyError
# from .util import dist, gon2rad, rad2gon




import bpy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEventLoop, Qt

from .gost import QtGostApp

context = None
 
 
# def launch():
    # # global context
    # # context = bpy.context.copy()
    # bpy.ops.wm.pyqt_event_loop()
 
 
# register class stuff
# class PyQtEventLoop(bpy.types.Operator):
    # bl_idname = "wm.pyqt_event_loop"
    # bl_label = "PyQt Event Loop"
    # _timer = None
    # _window = None
 
    # def execute(self, context):
        # self._application = QApplication.instance()
        # if self._application is None:
            # self._application = QApplication(['blender'])
        # self._eventLoop = QEventLoop()
        # return {'RUNNING_MODAL'}
 

class GostWindow(bpy.types.Operator):
    bl_idname = "tachy.gost_window"
    bl_label = "Main Gost Window"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        self._application = QApplication.instance()
        if self._application is None:
            self._application = QApplication(['blender'])
        self._eventLoop = QEventLoop()
        self.window = QtGostApp()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.window.show()
        return {'RUNNING_MODAL'}
        
class TachyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"
    bl_label = "Tachy Panel"

    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator("tachy.gost_window", text="Start GeOSurveyTool")
        # layout.operator_menu_enum("tachy.select_port", property="ports", text="Connect Tachymeter")
        # layout = self.layout.column(align=True)
        # layout.operator("tachy.station_point1", text="Station Point 1")
        # layout.operator("tachy.add_station_point", text="Add Station Point")
        # layout = self.layout.column(align=True)
        # layout.operator("tachy.set_station", text="Compute Station")
        # layout = self.layout.column(align=True)
        # layout.operator("tachy.measure_niv", text="Measure Nivellemnet")
        # layout.operator("tachy.measure_points", text="Measure Points")
        


                
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)

    
# def register():
    # bpy.utils.register_class(PyQtEventLoop)
# def unregister():
    # bpy.utils.unregister_class(PyQtEventLoop)
# try:
    # unregister()
# except:
    # pass
# register()
# launch()