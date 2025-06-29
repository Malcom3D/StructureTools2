import FreeCAD, App, FreeCADGui, Part, os, math
import Draft

from sympy import *
init_printing()

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class Surface:
    def __init__(self, obj, selection, Width, Height):
        for object in selection:
            if 'Line' in object.Name:
                self.x1 = round(object.Start.x, 2)
                self.y1 = round(object.Start.y, 2)
                self.z1 = round(object.Start.z, 2)
                self.x2 = round(object.End.x, 2)
                self.y2 = round(object.End.y, 2)
                self.z2 = round(object.End.z, 2)
                self.dist = float(str(object.Length).split()[0])
                alpha = atan2((y2-y1), (x2-x1))
                beta = atan2((x2-x1), (z2-z1))
                self.vec1 = App.Vector(self.x1,self.y1,self.z1)
                self.vec2 = App.Vector(self.x2, self.y2, self.z2)
                self.Width = Width
                self.Height = Height

    def execute(self, obj):
        # wire = make_wire(pointslist, closed=False, placement=None, face=None, support=None)

        #placement = App.Vector(self.x1,self.y1,self.z1)

        p1 = App.Vector(-self.Width/2, self.Height/2, 0)
        p2 = App.Vector(self.Width/2, self.Height/2, 0)
        p3 = App.Vector(self.Width/2, -self.Height/2, 0)
        p4 = App.Vector(-self.Width/2, -self.Height/2, 0)

        surface = Draft.make_wire([p1, p2, p3, p4], closed=True)
        surface.Placement = App.Placement(App.Vector(self.x1, self.y1, self.z1), App.Rotation(self.vec1, self.vec2))
        surface.Shape # is a face

        doc.recompute()
