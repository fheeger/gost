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

import numpy

def dist(x1,y1,x2,y2):
    return numpy.sqrt((x2-x1)**2+(y2-y1)**2)

def delta(x,y):
    return numpy.abs(x-y)
    
def gon2rad(g):
    return g*numpy.pi/200
    
def rad2gon(r):
    return r*200/numpy.pi
