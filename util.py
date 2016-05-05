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

import numpy as np
import bpy


def dist(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)


def delta(x,y):
    return np.abs(x-y)
    
    
def gon2rad(g):
    return g*np.pi/200


def rad2gon(r):
    return r*200/np.pi


def degr2rad(g):
    return g*np.pi/200
    
    
def rad2degr(r):
    return r*200/np.pi


def calc_angle_from_coords(a=[0,0,0], b=[0,0,0]):

    #Koordinatenlisten in Variablen wandeln:
    xa=a[0]
    ya=a[1]
    xb=b[0]
    yb=b[1]

    #Absoluter Abstand zwischen beiden Koordinaten:
    dist_ab = dist(a, b)

    #X und Y Differenz:
    xval=a[0]-b[0]
    yval=a[1]-b[1]

    #Gleichen sich Werte?
    if ya==yb:
        if xb>xa:
            angle_degr=90
        else:
            angle_degr=270
    elif xa==xb:
        if yb>ya:
            angle_degr=0
        else:
            angle_degr=180
    
    #Winkelfunktion erst in Radiant, dann in Grad:
    else:
        angle_rad = np.arctan(xval/yval)
        angle_degr = rad2degr(angle_rad)

    #In welchem Viertel befindet sich B von A ausgehen?
    if xa<xb and ya<yb:
        angle_degr = angle_degr
    elif xa<xb and ya>yb:
        angle_degr= angle_degr +180
    elif xa>xb and ya>yb:
        angle_degr= angle_degr +180
    elif xa>xb and ya<yb:
        angle_degr= angle_degr +360
        
    return(angle_degr, dist)


def append_polar(dist=[0.0], angle_degr=[0.0], coord=[0,0,0]):
    
    #Koordinaten liste als variablen ausgeben:
    xcoord=coord[0]
    ycoord=coord[1]
    
    angle_rad= degr2rad(angle_degr)
    
    #Distanz orthogonal errechnen:
    distx = np.sin(angle_rad)*dist
    disty = np.cos(angle_rad)*dist
    
    #Zieloordinaten 
    xnew=xcoord+distx
    ynew=ycoord+disty
    
    return(xnew, ynew)

def getSelectedObject():
    rv = None
    for obj in bpy.data.objects:
        if obj.select:
            if not rv is None:
                raise ValueError("More than one object selected")
            rv = obj
    return rv

def getContext():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        return {"window": window, "screen": screen, "area": area, "region": region}
