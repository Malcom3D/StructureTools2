import FreeCAD, App, FreeCADGui, Part, os, math
from PySide import QtWidgets, QtCore, QtGui
import subprocess

from sympy import *
init_printing()

ICONPATH = os.path.join(os.path.dirname(__file__), 'resources')

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Error icon
    msg_box.setWindowTitle('Error')
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class NTC2018:
    def __init__(self, selection):
        LoadPresence = 0
        for object in selection:
            if 'Load' in object.Name:
                LoadPresence = 1
                self.LinePreCalc(object)
                self.LoadPreCalc(object)

        for object in selection:
            if LoadPresence==0 and 'Line' in object.Name:
                self.LinePreCalc(object)

    def LinePreCalc(self, object):
        Owner=object.ObjectBase[0][0]
        x1 = round(Owner.Start.x, 2)
        y1 = round(Owner.Start.y, 2)
        z1 = round(Owner.Start.z, 2)
        x2 = round(Owner.End.x, 2)
        y2 = round(Owner.End.y, 2)
        z2 = round(Owner.End.z, 2)
        self.l = sqrt((x2-x1)**2+(y1-y2)**2+(z1-z2)**2)/1000

        # if is't parallel to xy-plane
        dist_alpha = sqrt((x2-x1)**2+(y2-y1)**2)
        alpha = atan2((z2-z1), dist_alpha)
        if not alpha==0:
            alpha = (pi/2 - alpha)
        self.alpha = alpha

    def LoadPreCalc(self, object):
        l = self.l
        alpha = self.alpha
        qa = 0
        qb = 0
        qa = float(str(object.FinalLoading).split(' ')[0])/1000000
        qb = float(str(object.InitialLoading).split(' ')[0])/1000000
        self.G2avr = (((qa+qb)/2)*cos(alpha)*l)
        qmax = max((((2*qa+qb)*cos(alpha))/3), (((qa+2*qb)*cos(alpha))/3))
        qmin = min((((2*qa+qb)*cos(alpha))/3), (((qa+2*qb)*cos(alpha))/3))
        # Reaction Ra and Rb
        Ra = (((2*qa+qb)*cos(alpha))*l)/6
        Rb = (((qa+2*qb)*cos(alpha))*l)/6
        # Shear force
        Va = Ra
        Vb = -Rb
        if qa==qb:
            # Bending moment
            x0 = Rational(1, 2)
            Mmax = (((qmax)*l**2)/2)
        else:
            z = qmin/qmax
            u = 0.577*sqrt(1+z+z**2)
            x0 = ((u-1)*l)/(z-1)
            # Bending moment
            Mmax = 0.1256*((((qa+qb)*cos(alpha))/2)*l**2)
        self.x0 = x0
        self.Mmax = Mmax
        # Normal stress

        #print('qa: ', qa, 'qb: ', qb, 'Ra: ', Ra, 'Rb: ', Rb, 'Va: ', Va, 'Vb: ', Vb, 'Mmax: ', Mmax, 'x0: ', x0, 'alpha: ', alpha, 'G2avr: ', self.G2avr, 'l: ', l, 'u: ', u, 'z: ', z, 'qmin: ', qmin, 'qmax: ', qmax)
