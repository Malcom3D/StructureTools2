import FreeCAD, App
import Draft

class Surface:
    def __init__(self, obj, selection, Width, Height):

        obj.Proxy = self

        for object in selection:
            if 'Line' in object.Name:
                self.x1 = object.Start.x, 2
                self.y1 = object.Start.y, 2
                self.z1 = object.Start.z, 2
                self.x2 = object.End.x, 2
                self.y2 = object.End.y, 2
                self.z2 = object.End.z, 2
                self.Width = Width
                self.Height = Height

                p1 = FreeCAD.Vector(-self.Width/2, self.Height/2, 0)
                p2 = FreeCAD.Vector(self.Width/2, self.Height/2, 0)
                p3 = FreeCAD.Vector(self.Width/2, -self.Height/2, 0)
                p4 = FreeCAD.Vector(-self.Width/2, -self.Height/2, 0)

                surface = Draft.make_wire([p1, p2, p3, p4], closed=True)

                v = App.Vector(x1,y1,z1).sub(App.Vector(x2,y2,z2))
                r = App.Rotation(App.Vector(0,0,1),v)
                pl = FreeCAD.Placement()
                pl.Rotation.Q = r.Q
                pl.Base = App.Vector(x1,y1,z1)
                surface.Placement = pl

    def execute(self, obj):
        pass

class ViewProviderSurface:
    def __init__(self, obj):
        pass

