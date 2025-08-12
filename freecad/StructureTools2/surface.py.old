import FreeCAD, App
import Draft

class Surface:
    def __init__(self, obj, selection, Width, Height):

        obj.Proxy = self

        for object in selection:
            if 'Line' in object.Name:
                x1 = object.Start.x
                y1 = object.Start.y
                z1 = object.Start.z
                x2 = object.End.x
                y2 = object.End.y
                z2 = object.End.z

                p1 = FreeCAD.Vector(-Width/2, Height/2, 0)
                p2 = FreeCAD.Vector(Width/2, Height/2, 0)
                p3 = FreeCAD.Vector(Width/2, -Height/2, 0)
                p4 = FreeCAD.Vector(-Width/2, -Height/2, 0)

                wire = Draft.make_wire([p1, p2, p3, p4], closed=True, face=True)

                v = FreeCAD.Vector(x1,y1,z1).sub(FreeCAD.Vector(x2,y2,z2))
                r = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),v)
                pl = FreeCAD.Placement()
                pl.Rotation.Q = r.Q
                pl.Base = FreeCAD.Vector(x1,y1,z1)
                wire.Placement = pl

    def execute(self, obj):
        pass

class ViewProviderSurface:
    def __init__(self, obj):
        pass

