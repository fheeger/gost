import numpy

def dist(x1,y1,x2,y2):
    return numpy.sqrt((x2-x1)**2+(y2-y1)**2)

def delta(x,y):
    return numpy.abs(x-y)
    
def gon2rad(g):
    return g*numpy.pi/200
    
def rad2gon(r):
    return r*200/numpy.pi
