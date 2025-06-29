import FreeCAD, App, FreeCADGui, Part, os, math
import Draft

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
                self.vec1 = FreeCAD.Vector(self.x1,self.y1,self.z1)
                self.vec2 = FreeCAD.Vector(self.x2, self.y2, self.z2)
                self.Width = Width
                self.Height = Height

    def execute(self, obj):
        # wire = make_wire(pointslist, closed=False, placement=None, face=None, support=None)

        #placement = App.Vector(self.x1,self.y1,self.z1)

        p1 = FreeCAD.Vector(-self.Width/2, self.Height/2, 0)
        p2 = FreeCAD.Vector(self.Width/2, self.Height/2, 0)
        p3 = FreeCAD.Vector(self.Width/2, -self.Height/2, 0)
        p4 = FreeCAD.Vector(-self.Width/2, -self.Height/2, 0)

        surface = Draft.make_wire([p1, p2, p3, p4], closed=True)
        surface.Placement = FreeCAD.Placement(FreeCAD.Vector(self.x1, self.y1, self.z1), FreeCAD.Rotation(self.vec1, self.vec2))
        surface.Shape # is a face

class ViewProviderSurface:
    def __init__(self, obj):
        pass

