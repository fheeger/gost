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


#plugin information for Blender
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
    

import bpy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEventLoop, Qt

from .gost import QtGostApp

#context = None
 

class GostWindow(bpy.types.Operator):
    """Mein Gost Window Class
    
    Subclassing Blender Operator to be displayed as a button.
    Starts the PyQt event loop and will show Gost main window when clicked.
    """
    bl_idname = "tachy.gost_window"
    bl_label = "Main Gost Window"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        self._application = QApplication.instance()
        if self._application is None:
            self._application = QApplication(['blender'])
        #create and start the PyQt event loop this is necessary,
        # because we are not using a normal PyQt setup
        self._eventLoop = QEventLoop()
        self.window = QtGostApp()
        #keep the window ontop of everything
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.window.show()
        return {'RUNNING_MODAL'}
        
class TachyPanel(bpy.types.Panel):
    """Blender panel to display the GOST button in"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"
    bl_label = "Tachy Panel"

    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator("tachy.gost_window", text="Start GeOSurveyTool")

                
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
