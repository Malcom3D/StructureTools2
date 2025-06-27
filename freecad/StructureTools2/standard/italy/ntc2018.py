import math

from sympy import *
init_printing()

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Error icon
    msg_box.setWindowTitle('Error')
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class NTC2018:
    def __init__(self, selection):
        self.G1avr = 0
        self.G2avr = 0
        self.g2load = 0
        self.length = 0
        self.alpha = 0
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
#        Owner=object.ObjectBase[0][0]
        Owner=object
        x1 = round(Owner.Start.x, 2)
        y1 = round(Owner.Start.y, 2)
        z1 = round(Owner.Start.z, 2)
        x2 = round(Owner.End.x, 2)
        y2 = round(Owner.End.y, 2)
        z2 = round(Owner.End.z, 2)
        self.length = sqrt((x2-x1)**2+(y1-y2)**2+(z1-z2)**2)/1000

        # if is't parallel to xy-plane
        dist_alpha = sqrt((x2-x1)**2+(y2-y1)**2)
        alpha = atan2((z2-z1), dist_alpha)
        if not alpha == 0:
            alpha = (pi/2 - alpha)
        self.alpha = alpha

    def LoadPreCalc(self, object):
        length = self.length
        alpha = self.alpha
        qa = 0
        qb = 0
        print(str(object.FinalLoading).split(' '))
        qa = float(str(object.FinalLoading).split(' ')[0])/1000000
        qb = float(str(object.InitialLoading).split(' ')[0])/1000000
        self.G2avr = (((qa+qb)/2)*cos(alpha)*length)
        qmax = max((((2*qa+qb)*cos(alpha))/3), (((qa+2*qb)*cos(alpha))/3))
        qmin = min((((2*qa+qb)*cos(alpha))/3), (((qa+2*qb)*cos(alpha))/3))
        # ntc2018 3.1.3
        for i in range(1,6):
            if i-1 < self.G2avr <= i:
                self.g2load = 0.4*i
        # Reaction Ra and Rb
        Ra = (((2*qa+qb)*cos(alpha))*length)/6
        Rb = (((qa+2*qb)*cos(alpha))*length)/6
        # Shear force
        Va = Ra
        Vb = -Rb
        if qa==qb:
            # Bending moment
            x0 = 0.5
            Mmax = (((qmax)*length**2)/2)
        else:
            z = qmin/qmax
            u = 0.577*sqrt(1+z+z**2)
            x0 = ((u-1)*length)/(z-1)
            # Bending moment
            Mmax = 0.1265*((((qa+qb)*cos(alpha))/2)*length**2)
        self.x0 = x0
        self.Mmax = Mmax

        #print('qa: ', qa, 'qb: ', qb, 'Ra: ', Ra, 'Rb: ', Rb, 'Va: ', Va, 'Vb: ', Vb, 'Mmax: ', Mmax, 'x0: ', x0, 'alpha: ', alpha, 'G2avr: ', self.G2avr, 'length: ', l, 'u: ', u, 'z: ', z, 'qmin: ', qmin, 'qmax: ', qmax)

    def FundComb(self, G1, GammaG1, G2, GammaG2, Q1, GammaQ1):
        Fd = G1*GammaG1+G2*GammaG2+Q1*GammaQ1
        return Fd
        
    def DesignRes(self, kmod, fxk, GammaM):
        desres = (kmod*fxk)/GammaM
        return desres

    def PreDim(self, Fd, interaxis, length, fmd, fvd):
        q = Fd*interaxis/1000 # N/m² * m = N/m to N/mm
        lengthmm = length*1000
#        bmin = (3*q*fmd)/(4*fvd**2)
#        hmin = ((lengthmm*fvd)/(fmd))
        bmin = ((7*q*lengthmm*fvd)/(20*fmd))
        hmin = sqrt((15*q*lengthmm)/(14*fvd))
#        hmin = cbrt((15*q*(lengthmm)**2)/(14*fmd))
#        bmin = 0.7*hmin
        return bmin, hmin

    def BeamWeight(self, Width, Height, Length, rhomean):
        # beam dead weight
        X = Width/1000 # mm to m
        Y = Height/1000 # mm to m
        Weightkg = (X*Y*Length)*rhomean
        WeightN = (Weightkg*9.80665)/1000 # kg to kN
        WeightQ = WeightN/(X*Length) # kN/m²
        print('BeamWeight: ', WeightN)
        return WeightN, WeightQ

    def MomentEq(self, Fd, interaxis, length, alpha):
        q = Fd*interaxis
        if cos(alpha) == 1:
            M = (q*length**2)/8
        elif cos(alpha) != 1 and cos(alpha) != 0:
            M = 0.1265*((q*cos(alpha))/2)*length**2
        return M

    def ShearForceEq(self, Fd, interaxis, length, alpha):
        q = Fd*interaxis
        if cos(alpha) == 1:
            V = q*length/2
        elif cos(alpha) != 1 and cos(alpha) != 0:
            V = ((q*cos(alpha))/2)*length
        return V

    def DeflectionEq(self, Fd, interaxis, Width, Height, length, alpha, E005):
        q = Fd*interaxis
        I = (Width*Height**3)/12
        if cos(alpha) == 1:
           f = (5/384)*((q*length**4)/(I*E005))
        elif cos(alpha) != 1 and cos(alpha) != 0:
           f = (5/384)*(((q*cos(alpha))*length**4)/(I*E005*cos(alpha)**2))
        return f

    def NormalStress(self, Fd, interaxis, length, alpha, Hk):
        q = Fd*interaxis
        if cos(alpha) == 1:
#            if A = cerniera B = appoggio semplice:
            N =  Hk
            return N
#            if A = appoggio semplice B = cerniera
        elif cos(alpha) != 1 and cos(alpha) != 0:
            N = Hk*sin(alpha)
            return N
#            if A = cerniera B = appoggio semplice:
#                Na = -(Hk*sin(alpha))*length
#                Nb = 0
#            if A = appoggio semplice B = cerniera
#                Na = 0
#                Nb = (Hk*sin(alpha))*length
#            if A = B = cerniera -> Na=Nb
#                N = -((Hk*sin(alpha)*length)/2
 

    def SectionModulus(self, Width, Heigh):
       Wmax = max(((Width*Heigh**2)/6), ((Heigh*Width**2)/6))
       Wmin = max(((Width*Heigh**2)/6), ((Heigh*Width**2)/6))
       return Wmax, Wmin

    def Verify_Bending(self, M, W, fmd):
        check = (M*1000000)/W
        if fmd <= check:
            return False
        else:
            return True

    def Verify_Shear(self, V, Width, Heigh, fvd):
        check = 3*V/(2*Width*Heigh)
        if fvd <= check:
            return False
        else:
            return True

    def Verify_NormalStress(self, N, Width, Heigh, fc0d, ft0d):
        check = N/(Width*Heigh)
        if N > 0:
            fx0d = ft0d
        else:
            fx0d = fc0d

        if fx0d <= check:
            return False
        else:
            return True

    def Verify_Deflection(self, f, length):
        check = length/300 
        if f > check:
            return False
        else:
            return True
