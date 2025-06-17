import FreeCAD, App, FreeCADGui, Part, os, math
from PySide import QtWidgets, QtCore, QtGui
import subprocess

from sympy import *
init_printing()

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Error icon
    msg_box.setWindowTitle("Error")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

def Size(Standard, G1Load, G2Load, Q1Load):
    doc = FreeCAD.ActiveDocument
    print(Standard, G1Load, G2Load, Q1Load)

def set_type(s):
    # Takes a string, inferes the type and returns either a string, int or float.
    if s.isnumeric():
        return int(s)
    if s.count(".") == 1 and "".join([c for c in s if c!="."]).isnumeric():
        return float(s)
    return s

class SizeTaskPanel:
    def __init__(self, widget, selection):
        self.form = [widget, QtGui.QDialog()]
        layoutStd = QtGui.QVBoxLayout()
        # Standard ComboBox
        self.form[0].setWindowTitle("Building Standard")
#        self.StandardLabel = QtGui.QLabel("Building Standard")
        self.StandardValue = QtGui.QComboBox()
        self.StandardValue.addItem('')
        self.StandardValue.addItem('Italy: ntc2018')
        self.StandardValue.addItem('Custom...')
        self.StandardValue.activated.connect(self.selectedStandard)

#        layoutStd.addWidget(self.StandardLabel)
        layoutStd.addWidget(self.StandardValue)
        self.form[0].setLayout(layoutStd)


        layout = QtGui.QVBoxLayout()

        for object in selection:
            if 'Load' in object.Name:
                Owner=object.ObjectBase[0][0]
                line = [[round(Owner.Start.x, 2), round(Owner.Start.y, 2), round(Owner.Start.z, 2)], [round(Owner.End.x, 2), round(Owner.End.y, 2), round(Owner.End.z, 2)]]
                x1 = round(Owner.Start.x, 2)
                y1 = round(Owner.Start.y, 2)
                z1 = round(Owner.Start.z, 2)
                x2 = round(Owner.End.x, 2)
                y2 = round(Owner.End.y, 2)
                z2 = round(Owner.End.z, 2)
                l = sqrt((x2-x1)**2+(y1-y2)**2+(z1-z2)**2)/1000

                # if is't parallel to xy-plane
                dist_alpha = sqrt((x2-x1)**2+(y2-y1)**2)
                alpha = atan2((z2-z1), dist_alpha)
                if not alpha==0:
                    alpha = (pi - alpha)
                qa = 0
                qb = 0
                qa = float(str(object.FinalLoading).split(" ")[0])/1000000
                qb = float(str(object.InitialLoading).split(" ")[0])/1000000
                Qavr = (((qa+qb)/2)*cos(alpha)*l)
            if (qa or qb) and not (qa==0 and qb==0):
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
                # Normal stress
            print('qa: ', qa, 'qb: ', qb, 'Ra: ', Ra, 'Rb: ', Rb, 'Va: ', Va, 'Vb: ', Vb, 'Mmax: ', Mmax, 'x0: ', x0, 'alpha: ', alpha, 'Qavr: ', Qavr, 'l: ', l, 'u: ', u, 'z: ', z, 'qmin: ', qmin, 'qmax: ', qmax)

        self.form[1].setWindowTitle("ntc2018")
        # Structural Load G1 [ntc2018 Tab. 3.1.I]
        self.G1LoadLabel = QtGui.QLabel("Structural load G1")
        self.G1LoadValue = QtGui.QDoubleSpinBox()
        self.G1LoadValue.setMaximum(99999999999999999999999999.99)
        print(Qavr)
        if Qavr:
            self.G1LoadValue.setValue(Qavr)
            self.G1LoadValue.setMinimum(Qavr)
        else:
            self.G1LoadValue.setValue(0)
        self.G1LoadValue.setSuffix(' kN/m²')
        self.G1LoadLabel.hide()
        self.G1LoadValue.hide()

        # Non Structural Load G2 [ntc2018 3.1.3]
        self.G2LoadLabel = QtGui.QLabel("Non structural load G2")
        self.G2LoadValue = QtGui.QDoubleSpinBox()
        self.G2LoadValue.setValue(0)
        self.G2LoadValue.setSuffix(' kN/m²')
        self.G2LoadLabel.hide()
        self.G2LoadValue.hide()

        # Overloads by intended use [ntc2018 Tab. 3.1.II]
        # - uniformly distributed vertical loads qk
        # - concentrated vertical loads Qk
        # - linear horizontal loads Hk

        # mapped list ['description', qk, Qk, Hk]
        self.Q1mapList = [list(map(set_type, ['', '0.0', '0.0', '0.0']))]
        self.Q1mapList.append(list(map(set_type, ['Cat.A  Areas for domestic and residential activities', '2.00', '2.00', '1.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.A  Common stairs, balconies, landings', '4.00', '4.00', '2.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B1 Offices not open to the public', '2.00', '2.00', '1.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B2 Offices open to the public', '3.00', '2.00', '1.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B  Common stairs, balconies and landings', '4.00', '4.00', '2.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C1 Areas with tables', '3.00', '3.00', '1.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C2 Areas with fixed seating', '4.00', '4.00', '2.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C3 Environments without obstacles to the movement of people', '5.00', '5.00', '3.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C4 Areas where physical activities may be carried out', '5.00', '5.00', '3.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C5 Areas susceptible to large crowds', '5.00', '5.00', '3.00'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C Common stairways, balconies and landings', '4.00', '4.00', '2.00'])))


        self.Q1LoadLabel = QtGui.QLabel("Overloads by intended use Q1")
        self.Q1LoadValue = QtGui.QComboBox()
        for i in range(0,len(self.Q1mapList[:])):
            self.Q1LoadValue.addItem(self.Q1mapList[i][0])
        self.Q1LoadValue.activated.connect(self.q1load)
        self.Q1LoadLabel.hide()
        self.Q1LoadValue.hide()

        self.qkLoadLabel = QtGui.QLabel("qk: 0 kN/m²")
        self.QkLoadLabel = QtGui.QLabel("Qk: 0 kN")
        self.HkLoadLabel = QtGui.QLabel("Hk: 0 kN/m")
        self.qkLoadLabel.hide()
        self.QkLoadLabel.hide()
        self.HkLoadLabel.hide()

        layout.addWidget(self.G1LoadLabel)
        layout.addWidget(self.G1LoadValue)
        layout.addWidget(self.G2LoadLabel)
        layout.addWidget(self.G2LoadValue)
        layout.addWidget(self.Q1LoadLabel)
        layout.addWidget(self.Q1LoadValue)
        layout.addWidget(self.qkLoadLabel)
        layout.addWidget(self.QkLoadLabel)
        layout.addWidget(self.HkLoadLabel)

        self.form[1].setLayout(layout)

    def selectedStandard(self, index):
        if index == 1:
            self.G1LoadLabel.show()
            self.G1LoadValue.show()
            self.G2LoadLabel.show()
            self.G2LoadValue.show()
            self.Q1LoadLabel.show()
            self.Q1LoadValue.show()
            self.qkLoadLabel.show()
            self.QkLoadLabel.show()
            self.HkLoadLabel.show()
        else:
            self.G1LoadLabel.hide()
            self.G1LoadValue.hide()
            self.G2LoadLabel.hide()
            self.G2LoadValue.hide()
            self.Q1LoadLabel.hide()
            self.Q1LoadValue.hide()
            self.qkLoadLabel.hide()
            self.QkLoadLabel.hide()
            self.HkLoadLabel.hide()

    def q1load(self, index):
        self.qk = self.Q1mapList[index][1]
        self.Qk = self.Q1mapList[index][2]
        self.Hk = self.Q1mapList[index][3]
        self.qkLoadLabel.setText('qk: ' + str(self.qk) + ' kN/m²')
        self.QkLoadLabel.setText('Qk: ' + str(self.Qk) + ' kN')
        self.HkLoadLabel.setText('Hk: ' + str(self.Hk) + ' kN/m')

    # Ok and Cancel buttons are created by default in FreeCAD Task Panels
    # What is done when we click on the ok button.
    def accept(self):
        Standard = self.StandardValue.currentText()
        G1Load = self.G1LoadValue.value()
        G2Load = self.G2LoadValue.value()
        Q1Load = [self.qk, self.Qk, self.Hk]

        Size(Standard, G1Load, G2Load, Q1Load)
        FreeCADGui.Control.closeDialog() #close the dialog

    # What is done when we click on the cancel button.
    # commented because this is the default behaviour
    #def reject(self):
    #   FreeCADGui.Control.closeDialog()


    def getIcon(self):
        return """
/* XPM */
static char *size[] = {
/* columns rows colors chars-per-pixel */
"32 32 191 2",
"   c black",
".  c #00E900E900E9",
"X  c #02C502C502C5",
"o  c #03AA03AA03AA",
"O  c #047804780478",
"+  c #04AD04AD04AD",
"@  c #081608160816",
"#  c #096809680968",
"$  c #0E900E900E90",
"%  c #13DA13DA13DA",
"&  c #161416141614",
"*  c #1B0F1B0F1B0F",
"=  c #1C011C011C01",
"-  c #1F4B1F4B1F4B",
";  c #234423442344",
":  c #238023802380",
">  c #23F923F923F9",
",  c #24D624D624D6",
"<  c #268F268F268F",
"1  c #26B126B126B1",
"2  c #277B277B277B",
"3  c #292E292E292E",
"4  c #298929892989",
"5  c #2A3D2A3D2A3D",
"6  c #2B3F2B3F2B3F",
"7  c #2D7C2D7C2D7C",
"8  c #2E882E882E88",
"9  c #2EAC2EAC2EAC",
"0  c #2EB02EB02EB0",
"q  c #2EB52EB52EB5",
"w  c #2EB92EB92EB9",
"e  c #30B430B430B4",
"r  c #30B830B830B8",
"t  c #30BD30BD30BD",
"y  c #317E317E317E",
"u  c #322732273227",
"i  c #325F325F325F",
"p  c #35C635C635C6",
"a  c #377937793779",
"s  c #3A583A583A58",
"d  c #3C873C873C87",
"f  c #3D1C3D1C3D1C",
"g  c #3D3F3D3F3D3F",
"h  c #3F883F883F88",
"j  c #402B402B402B",
"k  c #40BD40BD40BD",
"l  c #41EC41EC41EC",
"z  c #43B743B743B7",
"x  c #45EE45EE45EE",
"c  c #464A464A464A",
"v  c #46AB46AB46AB",
"b  c #494149414941",
"n  c #4FBF4FBF4FBF",
"m  c #4FCA4FCA4FCA",
"M  c #4FEF4FEF4FEF",
"N  c #527252725272",
"B  c #59D359D359D3",
"V  c #5A8E5A8E5A8E",
"C  c #5CE55CE55CE5",
"Z  c #5E495E495E49",
"A  c #600D600D600D",
"S  c #616961696169",
"D  c #619C619C619C",
"F  c #61D361D361D3",
"G  c #654965496549",
"H  c #65DF65DF65DF",
"J  c #670E670E670E",
"K  c #671867186718",
"L  c #68D468D468D4",
"P  c #6A3F6A3F6A3F",
"I  c #6DFA6DFA6DFA",
"U  c #6E7C6E7C6E7C",
"Y  c #6F396F396F39",
"T  c #6FAC6FAC6FAC",
"R  c #706670667066",
"E  c #713C713C713C",
"W  c #72FA72FA72FA",
"Q  c #749D749D749D",
"!  c #74B474B474B4",
"~  c #758975897589",
"^  c #765C765C765C",
"/  c #781178117811",
"(  c #788378837883",
")  c #7AAF7AAF7AAF",
"_  c #7B377B377B37",
"`  c #7BC57BC57BC5",
"'  c #7D8B7D8B7D8B",
"]  c #7EE07EE07EE0",
"[  c #7EE17EE17EE1",
"{  c #7F387F387F38",
"}  c #81F681F681F6",
"|  c #846184618461",
" . c #850A850A850A",
".. c #854485448544",
"X. c #858485848584",
"o. c #86C586C586C5",
"O. c #876A876A876A",
"+. c #87E087E087E0",
"@. c #88E888E888E8",
"#. c #892489248924",
"$. c #8A638A638A63",
"%. c #8B7C8B7C8B7C",
"&. c #8DCE8DCE8DCE",
"*. c #901B901B901B",
"=. c #926192619261",
"-. c #928592859285",
";. c #948A948A948A",
":. c #94A294A294A2",
">. c #96DC96DC96DC",
",. c #989198919891",
"<. c #990499049904",
"1. c #991199119911",
"2. c #9B409B409B40",
"3. c #9B879B879B87",
"4. c #9C699C699C69",
"5. c #9D689D689D68",
"6. c #9F059F059F05",
"7. c #9F8B9F8B9F8B",
"8. c #9FC09FC09FC0",
"9. c #A024A024A024",
"0. c #A0E5A0E5A0E5",
"q. c #A1A7A1A7A1A7",
"w. c #A3BEA3BEA3BE",
"e. c #A7ABA7ABA7AB",
"r. c #A923A923A923",
"t. c #A983A983A983",
"y. c #AA8FAA8FAA8F",
"u. c #AB4FAB4FAB4F",
"i. c #AD12AD12AD12",
"p. c #ADCAADCAADCA",
"a. c #B032B032B032",
"s. c #B8EFB8EFB8EF",
"d. c #B911B911B911",
"f. c #BA0EBA0EBA0E",
"g. c #BC23BC23BC23",
"h. c #BC82BC82BC82",
"j. c #BCC2BCC2BCC2",
"k. c #BCF3BCF3BCF3",
"l. c #BD9FBD9FBD9F",
"z. c #C035C035C035",
"x. c #C121C121C121",
"c. c #C22DC22DC22D",
"v. c #C603C603C603",
"b. c #CB89CB89CB89",
"n. c #CC78CC78CC78",
"m. c #D084D084D084",
"M. c #D0C0D0C0D0C0",
"N. c #D17BD17BD17B",
"B. c #D481D481D481",
"V. c #D5D3D5D3D5D3",
"C. c #D5EED5EED5EE",
"Z. c #DA03DA03DA03",
"A. c #DB11DB11DB11",
"S. c #DCDADCDADCDA",
"D. c #DF64DF64DF64",
"F. c #E010E010E010",
"G. c #E2A1E2A1E2A1",
"H. c #E36CE36CE36C",
"J. c #E424E424E424",
"K. c #E5BAE5BAE5BA",
"L. c #E7A0E7A0E7A0",
"P. c #E891E891E891",
"I. c #E9CBE9CBE9CB",
"U. c #E9D3E9D3E9D3",
"Y. c #EA55EA55EA55",
"T. c #EC01EC01EC01",
"R. c #EDEAEDEAEDEA",
"E. c #EE88EE88EE88",
"W. c #EEABEEABEEAB",
"Q. c #F344F344F344",
"!. c #F3CFF3CFF3CF",
"~. c #F444F444F444",
"^. c #F6E5F6E5F6E5",
"/. c #F6F1F6F1F6F1",
"(. c #F920F920F920",
"). c #FA10FA10FA10",
"_. c #FA86FA86FA86",
"`. c #FA98FA98FA98",
"'. c #FB14FB14FB14",
"]. c #FB36FB36FB36",
"[. c #FCA2FCA2FCA2",
"{. c #FD4EFD4EFD4E",
"}. c #FD87FD87FD87",
"|. c #FE61FE61FE61",
" X c #FEA4FEA4FEA4",
".X c #FEF7FEF7FEF7",
"XX c #FF15FF15FF15",
"oX c #FF32FF32FF32",
"OX c #FFBBFFBBFFBB",
"+X c #FFF3FFF3FFF3",
"@X c gray100",
/* pixels */
"@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X:   g 3 N ~.@X@X@X@X@X@X@X@X@X@X",
"@X@X@X@X@X@X@X@X@X@X@X@X-.% @ OX2         p @X@X@X@X@X@X@X@X@X@X",
"@X@X@X@X@X@X@X@XA.O.o _.B     G.8.l ,.#   T.h.t.@X@X@X@X@X@X@X@X",
"@X@X@X@X}.B.` W.X.    b.z.  M C.@X@X@X^.N.J.    P @X@X@X@X@X@X@X",
"@X@X@X@Xy.    p.Z.    +.@X@X@X@X@X@X@X@X@X0.    @.@X@X@X@X@X@X@X",
"@X@X@Xa.s     u @X@X@X@Xk z v ] @X@X@X@X@X@Xm.j  X_   f.@X@X@X@X",
"@X@X@X@Xd     [ @X@X@X@X      R @X@X@X@X@X@X@X@Xg.      @X@X@X@X",
"@X@X@Xs.S 1 < [...c E.@X      W @X@X@X@X@X@X@X@X.X.       @X@X@X",
"@X@X@Xr.    @Xv.      @X      ~ @X@X@X@X@Xb   H @X        @X@X@X",
"@X@X@Xr.    @XF.=   j.I.      / @X .$ i @X      @Xh 7 ; w @X@X@X",
"@X@X@X@X@X@X@X@X].6.@Xa         oX8     @XE & $.@X@X@X@X@X@X@X@X",
"@X@X@Xs.G G @X@X@X@X@X          H.3.  m @X@X@X@X@X@X^     @X@X@X",
"@X@X@Xr.    @X@X@X@X@XU.      + k.@X@X@X@X@X@X@X@X@X!     @X@X@X",
"@X@X@Xr.    @X@X@X@X@X@X      } @X@X@X@X@X@X@X@X@X@X) t q @X@X@X",
"@X@X@X@X@X@X@X@X@X@X@X@X      | @X@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X",
"@X@X@Xs.G G @X@X@X@X@X@X      o.@X@X@X@X@X@X@X@X@X@XT     @X@X@X",
"@X@X@Xr.    @X@X@X@X@X@X      #.@X@X@X@X@X@X@X@X@X@XI     @X@X@X",
"@X@X@Xr.    @X@X@X@X@X@X      %.@X@X@X@X@X@X@X@X@X@XQ r 0 @X@X@X",
"@X@X@X@X@X@X@X@X@X@X@X@X      &.@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X",
"@X@X@Xs.G G @X@X@X@X@X@X      *.@X@X@X@X@X@X@X@X@X@XL     @X@X@X",
"@XP.( e.    @X@X@X@X@X@X      =.@X@X@X@X@X@X@X@X@X@XK     @X@X@X",
"(.-   5     @X@X@X@X@X@X      :.@X@X@X@X@X@X@X@X@X@XU e 9 @X@X@X",
"C         S.@X@X@X@X@X@X      >.@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X@X",
"            l.@X@X@X@X@X      1.@X@X@X@X@X@X@X@X@X@XF     @X@X@X",
"6             ;.+X@X@X@X      2.@X@X@X@X@X@X@X@X@X@XA     K.4.> ",
"'.J             D ).@X@X      5.@X@X@X@X@X@X@X@X@XXXV * X       ",
"@X@X<.            , Y.@X      7.@X@X@X@X@X@X{.V.{               ",
"@X@X@Xx.              M.      q.@X@X@X`.n.Y                     ",
"@X@X@X@XD.O                   w./.c.Z                           ",
"@X@X@X@X@X!.x                 y                           4 9.L.",
"@X@X@X@X@X@X|.'                                     f i.R.@X@X@X",
"@X@X@X@X@X@X@X@Xu.                            n d.Q.@X@X@X@X@X@X"
};
		"""


class CommandSize():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/size.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+S", # a default shortcut (optional)
                "MenuText": "size structure",
                "ToolTip" : "Size the structure"}
    
    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        doc = FreeCAD.ActiveDocument
#        obj = doc.addObject("Part::FeaturePython", "Size")
#        objSuport = Size(obj, selection)
#        ViewProviderSize(obj.ViewObject)           

        # what is done when the command is clicked
        # creates a panel with a dialog
        baseWidget = QtGui.QWidget()
        panel = SizeTaskPanel(baseWidget, selection)
        # having a panel with a widget in self.form and the accept and 
        # reject functions (if needed), we can open it:
        FreeCADGui.Control.showDialog(panel)


        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("size", CommandSize())
