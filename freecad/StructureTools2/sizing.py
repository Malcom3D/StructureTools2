import FreeCAD, App, FreeCADGui, Part, os, math
#import Draft
from PySide import QtWidgets, QtCore, QtGui
import subprocess

from freecad.StructureTools2.standard.italy.ntc2018 import NTC2018
from freecad.StructureTools2.standard.italy.constant import Constant
from freecad.StructureTools2.material import Material, ViewProviderMaterial
#from freecad.StructureTools2.surface import Surface, ViewProviderSurface

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

def Size(Standard, G1Load, G2Load, Q1Load):
    doc = FreeCAD.ActiveDocument
    #print(Standard, G1Load, G2Load, Q1Load)

def set_type(s):
    # Takes a string, inferes the type and returns either a string, int or float.
    if isinstance(s, int) or isinstance(s, float):
        return s
    if s.isnumeric():
        return int(s)
    if s.count('.') == 1 and ''.join([c for c in s if c!='.']).isnumeric():
        return float(s)
    return s

class Sizing:
    def __init__(self, selection):
        self.selection = selection
        for object in self.selection:
            if 'NewProject' in object.Name:
                if 'ntc2018' in object.BuildingStandard:
                    self.BuildingStandard = object.BuildingStandard
                    self.Latitude = object.Latitude
                    self.Longitude = object.Longitude
                    self.Elevation = object.Elevation
                    self.Vn = object.Vn
                    self.Cu = object.Cu

        self.NTC2018Data = NTC2018(self.selection)
        self.G1avr = self.NTC2018Data.G1avr
        self.G2avr = self.NTC2018Data.G2avr
        self.G2load = self.NTC2018Data.G2load
        self.length = self.NTC2018Data.length
        self.alpha = self.NTC2018Data.alpha

        self.constant = Constant()
        self.Q1mapList = self.constant.Q1map()
        self.StrengthList = self.constant.Strength()
        self.GammaList = self.constant.Gamma()
        self.GammaMList = self.constant.GammaM()
        self.KdefList = self.constant.Kdef()
        self.KmodList = self.constant.Kmod()
        self.BeamDimList = self.constant.BeamDim()

        self.qk = 0
        self.Qk = 0
        self.Hk = 0

        self.fmk = 0
        self.ft0k = 0
        self.ft90k = 0
        self.fc0k = 0
        self.fc90k = 0
        self.fvk = 0
        self.E0mean = 0
        self.E005 = 0
        self.E90mean = 0
        self.Gmean = 0
        self.rk = 0
        self.rmean = 0

        self.kmodPerm = 0
        self.kmodLongPerm = 0
        self.kmodMed = 0
        self.kmodShort = 0
        self.kmodInst = 0

        self.GammaM = 1
        self.interaxis = 1
        self.bmin = 0
        self.hmin  = 0
        self.B = 0
        self.H = 0
        self.selWidth = 0
        self.selHeight = 0

        self.beamQ = 0
        self.beamminQ = 0
        self.beamweight = 0
        self.oldbeamweight = 0
        self.FinalBeamDim = 0

        self.form = QtGui.QDialog()
        self.LoadParam()

    def LoadParam(self):
        # ntc2018 Load Parameter QDialog
        self.form.setWindowTitle('Load Parameter:')
        layout = QtGui.QVBoxLayout()
        # Structural Load G1 [ntc2018 Tab. 3.1.I]
        self.G1LoadLabel = QtGui.QLabel('Structural load G1 [ntc2018 Tab. 3.1.I]')
        self.G1LoadValue = QtGui.QDoubleSpinBox()
        self.G1LoadValue.setMaximum(999999999999.99)
        if self.G1avr:
            self.G1LoadValue.setValue(self.G1avr)
            self.G1LoadValue.setMinimum(self.G1avr)
        else:
            self.G1LoadValue.setValue(0)
        self.G1LoadValue.setDecimals(4)
        self.G1LoadValue.setSuffix(' kN/m²')
        self.G1LoadValue.valueChanged.connect(self.DimBoundaries)

        # Non Structural Load G2 [ntc2018 3.1.3]
        self.G2LoadLabel = QtGui.QLabel('Non structural load G2 [ntc2018 3.1.3]')
        self.G2LoadValue = QtGui.QDoubleSpinBox()
        self.G2LoadValue.setMaximum(999999999999.99)
        if self.G2avr:
            self.G2LoadValue.setValue(self.G2avr)
            self.G2LoadValue.setMinimum(self.G2avr)
        else:
            self.G2LoadValue.setValue(0)
        self.G2LoadValue.setDecimals(4)
        self.G2LoadValue.setSuffix(' kN/m²')
        self.G2LoadValue.valueChanged.connect(self.DimBoundaries)

        self.Q1LoadLabel = QtGui.QLabel('Overloads by intended use Q1 [ntc2018 Tab. 3.1.II]')
        self.Q1LoadValue = QtGui.QComboBox()
        for i in range(0,len(self.Q1mapList[:])):
            self.Q1LoadValue.addItem(self.Q1mapList[i][0])
        self.Q1LoadValue.activated.connect(self.q1load)

        self.qkLoadValue = QtGui.QDoubleSpinBox()
        self.qkLoadValue.setPrefix('qk: ')
        self.qkLoadValue.setSuffix(' kN/m²')
        self.qkLoadValue.setMinimum(0)
        self.qkLoadValue.setMaximum(0)

        self.QkLoadValue = QtGui.QDoubleSpinBox()
        self.QkLoadValue.setPrefix('Qk: ')
        self.QkLoadValue.setSuffix(' kN')
        self.QkLoadValue.setMinimum(0)
        self.QkLoadValue.setMaximum(0)

        self.HkLoadValue = QtGui.QDoubleSpinBox()
        self.HkLoadValue.setPrefix('Hk: ')
        self.HkLoadValue.setSuffix(' kN/m')
        self.HkLoadValue.setMinimum(0)
        self.HkLoadValue.setMaximum(0)

        self.MaterialLabel = QtGui.QLabel('Material')
        self.MaterialValue = QtGui.QComboBox()
        self.MaterialValue.addItem('')
        self.MaterialValue.addItem('Wood')
        self.MaterialValue.addItem('Reinforced concrete')
        self.MaterialValue.addItem('Steel')
        self.MaterialValue.activated.connect(self.selectedMaterial)

        layout.addWidget(self.G1LoadLabel)
        layout.addWidget(self.G1LoadValue)
        layout.addWidget(self.G2LoadLabel)
        layout.addWidget(self.G2LoadValue)
        layout.addWidget(self.Q1LoadLabel)
        layout.addWidget(self.Q1LoadValue)
        layout.addWidget(self.qkLoadValue)
        layout.addWidget(self.QkLoadValue)
        layout.addWidget(self.HkLoadValue)
        layout.addWidget(self.MaterialLabel)
        layout.addWidget(self.MaterialValue)

####################################################################

        # Wood Material parameter
        layoutWood = QtGui.QVBoxLayout()
        layoutWoodParam = QtGui.QHBoxLayout()
        layoutWoodParamCol1 = QtGui.QVBoxLayout()
        layoutWoodParamCol2 = QtGui.QVBoxLayout()

        self.WoodTypeLabel = QtGui.QLabel('Wood Type')
        self.WoodTypeValue = QtGui.QComboBox()
        text = ''
        self.WoodTypeValue.addItem(text)
        for i in range(0,len(self.KmodList[:])):
            if self.KmodList[i][0] not in text:
                text = self.KmodList[i][0]
                self.WoodTypeValue.addItem(text)
        self.WoodTypeValue.activated.connect(self.selectedWoodType)

        self.WoodClassLabel = QtGui.QLabel('Wood Class')
        self.WoodClassValue = QtGui.QComboBox()
        self.WoodClassValue.activated.connect(self.selectedWoodClass)

        self.kmodPermLabel = QtGui.QLabel('Permanent Kmod: 0')
        self.kmodLongLabel = QtGui.QLabel('Long Kmod: 0')
        self.kmodMedLabel = QtGui.QLabel('Medium Kmod: 0')
        self.kmodShortLabel = QtGui.QLabel('Short Kmod: 0')
        self.kmodInstLabel = QtGui.QLabel('Instant Kmod: 0')

        layoutWoodParamCol1.addWidget(self.kmodPermLabel)
        layoutWoodParamCol1.addWidget(self.kmodLongLabel)
        layoutWoodParamCol1.addWidget(self.kmodMedLabel)

        layoutWoodParamCol2.addWidget(self.kmodShortLabel)
        layoutWoodParamCol2.addWidget(self.kmodInstLabel)

        self.formWood = QtGui.QDialog()
        self.formWoodParam = QtGui.QDialog()
        self.formWoodParamCol1 = QtGui.QDialog()
        self.formWoodParamCol2 = QtGui.QDialog()

        self.formWoodParamCol1.setLayout(layoutWoodParamCol1)
        self.formWoodParamCol2.setLayout(layoutWoodParamCol2)

        layoutWoodParam.addWidget(self.formWoodParamCol1)
        layoutWoodParam.addWidget(self.formWoodParamCol2)

        self.formWoodParam.setLayout(layoutWoodParam)

        layoutWood.addWidget(self.WoodTypeLabel)
        layoutWood.addWidget(self.WoodTypeValue)
        layoutWood.addWidget(self.WoodClassLabel)
        layoutWood.addWidget(self.WoodClassValue)
        layoutWood.addWidget(self.formWoodParam)

        self.formWood.setLayout(layoutWood)
        self.formWood.hide()
        layout.addWidget(self.formWood)

#####################################################################################

        # Wood Strength parameter
        self.formMaterial = QtGui.QDialog()
        layoutMaterial = QtGui.QVBoxLayout()
        layoutMatParam = QtGui.QHBoxLayout()
        layoutMatParamCol1 = QtGui.QVBoxLayout()
        layoutMatParamCol2 = QtGui.QVBoxLayout()

        self.StrengthLabel = QtGui.QLabel('Strength class')
        self.StrengthValue = QtGui.QComboBox()
        for i in range(0,len(self.StrengthList[:])):
            self.StrengthValue.addItem(self.StrengthList[i][0])
        self.StrengthValue.activated.connect(self.selectedStrength)

        self.fmkLabel = QtGui.QLabel('fmk: 0 kN/mm²')
        self.ft0kLabel = QtGui.QLabel('ft0k: 0 kN/mm²')
        self.ft90kLabel = QtGui.QLabel('ft90k: 0 kN/mm²')
        self.fc0kLabel = QtGui.QLabel('fc0k: 0 kN/mm²')
        self.fc90kLabel = QtGui.QLabel('fc90k: 0 kN/mm²')
        self.fvkLabel = QtGui.QLabel('fvk: 0 kN/mm²')
        self.E0meanLabel = QtGui.QLabel('E0mean: 0 kN/mm²')
        self.E005Label = QtGui.QLabel('E005: 0 kN/mm²')
        self.E90meanLabel = QtGui.QLabel('E90mean: 0 kN/mm²')
        self.GmeanLabel = QtGui.QLabel('Gmean: 0 kN/mm²')
        self.rkLabel = QtGui.QLabel('rk: 0 kg/m³')
        self.rmeanLabel = QtGui.QLabel('rmean: 0 kg/m³')

        layoutMatParamCol1.addWidget(self.fmkLabel)
        layoutMatParamCol1.addWidget(self.ft0kLabel)
        layoutMatParamCol1.addWidget(self.ft90kLabel)
        layoutMatParamCol1.addWidget(self.fc0kLabel)
        layoutMatParamCol1.addWidget(self.fc90kLabel)
        layoutMatParamCol1.addWidget(self.fvkLabel)

        layoutMatParamCol2.addWidget(self.E0meanLabel)
        layoutMatParamCol2.addWidget(self.E005Label)
        layoutMatParamCol2.addWidget(self.E90meanLabel)
        layoutMatParamCol2.addWidget(self.GmeanLabel)
        layoutMatParamCol2.addWidget(self.rkLabel)
        layoutMatParamCol2.addWidget(self.rmeanLabel)

        self.formMatParam = QtGui.QDialog()
        self.formMatParamCol1 = QtGui.QDialog()
        self.formMatParamCol2 = QtGui.QDialog()

        self.formMatParamCol1.setLayout(layoutMatParamCol1)
        self.formMatParamCol2.setLayout(layoutMatParamCol2)

        layoutMatParam.addWidget(self.formMatParamCol1)
        layoutMatParam.addWidget(self.formMatParamCol2)

        self.formMatParam.setLayout(layoutMatParam)

        layoutMaterial.addWidget(self.StrengthLabel)
        layoutMaterial.addWidget(self.StrengthValue)
        layoutMaterial.addWidget(self.formMatParam)

        self.formMaterial.setLayout(layoutMaterial)
        self.formMaterial.hide()
        layout.addWidget(self.formMaterial)

###########################################################################

        # beams step and Area of influence
        self.formPreSizing = QtGui.QDialog()
        layoutPreSize = QtGui.QVBoxLayout()
        self.BeamStepLabel = QtGui.QLabel('Beam step')
        self.BeamStepValue = QtGui.QDoubleSpinBox()
        self.BeamStepValue.setDecimals(4)
        self.BeamStepValue.setSuffix(' m')
        self.BeamStepValue.setMinimum(0.0001)
        self.BeamStepValue.setMaximum(9999999999.9999)
        self.BeamStepValue.setValue(1/self.length)
        self.BeamStepValue.valueChanged.connect(self.selectedBeamStep)

        self.InfluenceAreaLabel = QtGui.QLabel('Area of influence')
        self.InfluenceAreaValue = QtGui.QDoubleSpinBox()
        self.InfluenceAreaValue.setDecimals(4)
        self.InfluenceAreaValue.setSuffix(' m²')
        self.InfluenceAreaValue.setMaximum(9999999999.9999)
        self.InfluenceAreaValue.setMinimum(0.0001)
        self.InfluenceAreaValue.setValue(1)
        self.InfluenceAreaValue.valueChanged.connect(self.selectedInfluenceArea)

        layoutPreSize.addWidget(self.BeamStepLabel)
        layoutPreSize.addWidget(self.BeamStepValue)
        layoutPreSize.addWidget(self.InfluenceAreaLabel)
        layoutPreSize.addWidget(self.InfluenceAreaValue)

        self.formPreSizing.setLayout(layoutPreSize)
        self.formPreSizing.hide()
        layout.addWidget(self.formPreSizing)

###########################################################################

        # Design resistances [fc0d, fmd, fvd]
        self.formDesRes = QtGui.QDialog()
        layoutDesRes = QtGui.QVBoxLayout()

        self.DesignResistance = QtGui.QLabel('Design resistances')
        self.NormalStressLabel = QtGui.QLabel('Normal stress fc0d: 0 kN/mm²')
        self.BendingLabel = QtGui.QLabel('Bending fmd: 0 kN/mm²')
        self.ShearLabel = QtGui.QLabel('Shear fvd: 0 kN/mm²')

        self.WidthMinLabel = QtGui.QLabel('Section width minimum: 0 mm')
        self.HeightMinLabel = QtGui.QLabel('Section height minimum: 0 mm')

        self.FundCombLabel = QtGui.QLabel('Fundamental Combination: 0 kN/m²')

        self.BeamMinWeightLabel = QtGui.QLabel('Minimum section weight: 0 kN')


        self.SelectedWidthLabel = QtGui.QLabel('Selected width: 0 mm')
        self.SelectedHeightLabel = QtGui.QLabel('Selected height: 0  mm')
        self.BeamWeightLabel = QtGui.QLabel('Selected section weight: 0 kN')

        layoutDesRes.addWidget(self.DesignResistance)
        layoutDesRes.addWidget(self.NormalStressLabel)
        layoutDesRes.addWidget(self.BendingLabel)
        layoutDesRes.addWidget(self.ShearLabel)
        layoutDesRes.addWidget(self.WidthMinLabel)
        layoutDesRes.addWidget(self.HeightMinLabel)
        layoutDesRes.addWidget(self.FundCombLabel)
        layoutDesRes.addWidget(self.BeamMinWeightLabel)
        layoutDesRes.addWidget(self.SelectedWidthLabel)
        layoutDesRes.addWidget(self.SelectedHeightLabel)
        layoutDesRes.addWidget(self.BeamWeightLabel)

        self.formDesRes.setLayout(layoutDesRes)
        layout.addWidget(self.formDesRes)

#############################################################################

        # Design resistances [fc0d, fmd, fvd]
        self.formDimComm = QtGui.QDialog()
        layoutDimComm = QtGui.QVBoxLayout()

        self.DimCommLabel = QtGui.QLabel('Beam of commercial dimensions')
        self.DimCommValue = QtGui.QComboBox()
        text = ''
        self.DimCommValue.addItem(text)
        if self.bmin and self.bmax:
             print('self.formDimComm self.BeamComDimm')
             self.BeamComDimm()
        self.DimCommValue.activated.connect(self.selectedDimComm)

        self.DimCommXValue = QtGui.QDoubleSpinBox()
        self.DimCommXValue.setDecimals(2)
        self.DimCommXValue.setPrefix('B ')
        self.DimCommXValue.setSuffix(' mm')
        self.DimCommXValue.setMinimum(self.bmin)
        self.DimCommXValue.setMaximum(999999999999.99)
        self.DimCommXValue.valueChanged.connect(self.selectedDimCommXY)
        self.DimCommXValue.hide()

        self.DimCommYValue = QtGui.QDoubleSpinBox()
        self.DimCommYValue.setDecimals(2)
        self.DimCommYValue.setPrefix('H ')
        self.DimCommYValue.setSuffix(' mm')
        self.DimCommYValue.setMinimum(self.hmin)
        self.DimCommYValue.setMaximum(999999999999.99)
        self.DimCommYValue.valueChanged.connect(self.selectedDimCommXY)
        self.DimCommYValue.hide()

        layoutDimComm.addWidget(self.DimCommValue)
        layoutDimComm.addWidget(self.DimCommXValue)
        layoutDimComm.addWidget(self.DimCommYValue)

        self.formDimComm.setLayout(layoutDimComm)
        layout.addWidget(self.formDimComm)

#############################################################################

        self.form.setLayout(layout)

#############################################################################

    def q1load(self):
        index = self.Q1LoadValue.currentIndex()
        self.psiList = self.constant.psi(index, self.Elevation)

        # ntc2018 3.1.4
        self.qk = self.Q1mapList[index][1]
        self.Qk = self.Q1mapList[index][2]
        self.Hk = self.Q1mapList[index][3]
        IndexCount = self.Q1LoadValue.count() -1
        if index == IndexCount:
            self.qkLoadValue.setMinimum(self.qk)
            self.qkLoadValue.setMaximum(999999999999.99)
            self.QkLoadValue.setMinimum(self.Qk)
            self.QkLoadValue.setMaximum(999999999999.99)
            self.HkLoadValue.setMinimum(self.Hk)
            self.HkLoadValue.setMaximum(999999999999.99)
        else:
            self.qkLoadValue.setMinimum(self.qk)
            self.qkLoadValue.setMaximum(self.qk)
            self.QkLoadValue.setMinimum(self.Qk)
            self.QkLoadValue.setMaximum(self.Qk)
            self.HkLoadValue.setMinimum(self.Hk)
            self.HkLoadValue.setMaximum(self.Hk)

        self.DimBoundaries(0)

    def selectedMaterial(self):
        index = self.MaterialValue.currentIndex()
        if index == 1:
            self.formWood.show()
            self.DimBoundaries(0)
            #self.formConcrete.hide()
            #self.formSteel.hide()
        elif index == 2:
            self.formWood.hide()
            self.formMaterial.hide()
            self.formPreSizing.hide()
            #self.formConcrete.hide()
            #self.formSteel.show()
        elif index == 3:
            self.formWood.hide()
            self.formMaterial.hide()
            self.formPreSizing.hide()
            #self.formConcrete.hide()
            #self.formSteel.show()

    def selectedWoodType(self):
        self.WoodClassValue.clear()
        text = ''
        self.WoodClassValue.addItem(text)
        for i in range(0,len(self.KmodList[:])):
            if self.KmodList[i][0] == self.WoodTypeValue.currentText():
                text = 'Class ' + str(self.KmodList[i][2]) + ' : ' + self.KmodList[i][1]
                self.WoodClassValue.addItem(text)

        self.DimBoundaries(0)

    def selectedWoodClass(self):
        index = self.WoodClassValue.currentIndex()
        if index == 0:
            self.formMaterial.hide()
        else:
            self.formMaterial.show()

            for i in range(0,len(self.KmodList[:])):
                if self.KmodList[i][0] in self.WoodTypeValue.currentText():
                    self.kmodPerm = self.KmodList[i][3]
                    self.kmodLongPerm = self.KmodList[i][4]
                    self.kmodMed = self.KmodList[i][5]
                    self.kmodShort = self.KmodList[i][6]
                    self.kmodInst = self.KmodList[i][7]

                    self.kmodPermLabel.setText('Permanent Kmod: ' + str(self.kmodPerm))
                    self.kmodLongLabel.setText('Long Kmod: ' + str(self.kmodLongPerm))
                    self.kmodMedLabel.setText('Medium Kmod: ' + str(self.kmodMed))
                    self.kmodShortLabel.setText('Short Kmod: ' + str(self.kmodShort))
                    self.kmodInstLabel.setText('Instant Kmod: ' + str(self.kmodInst))

            self.DimBoundaries(0)

    def selectedStrength(self):
        index = self.StrengthValue.currentIndex()
        if index == 0:
            self.formPreSizing.hide()
        else:
            self.formPreSizing.show()

            self.fmk = self.StrengthList[index][1]
            self.ft0k = self.StrengthList[index][2]
            self.ft90k = self.StrengthList[index][3]
            self.fc0k = self.StrengthList[index][4]
            self.fc90k = self.StrengthList[index][5]
            self.fvk = self.StrengthList[index][6]
            self.E0mean = self.StrengthList[index][7]
            self.E005 = self.StrengthList[index][8]
            self.E90mean = self.StrengthList[index][9]
            self.Gmean = self.StrengthList[index][10]
            self.rk = self.StrengthList[index][11]
            self.rmean = self.StrengthList[index][12]

            self.fmkLabel.setText('fmk: ' + str(self.fmk) + ' N/mm²')
            self.ft0kLabel.setText('ft0k: ' + str(self.ft0k) + ' N/mm²')
            self.ft90kLabel.setText('ft90k: ' + str(self.ft90k) + ' N/mm²')
            self.fc0kLabel.setText('fc0k: ' + str(self.fc0k) + ' N/mm²')
            self.fc90kLabel.setText('fc90k: ' + str(self.fc90k) + ' N/mm²')
            self.fvkLabel.setText('fvk: ' + str(self.fvk) + ' N/mm²')
            self.E0meanLabel.setText('E0mean: ' + str(self.E0mean) + ' kN/mm²')
            self.E005Label.setText('E005: ' + str(self.E005) + ' kN/mm²')
            self.E90meanLabel.setText('E90mean: ' + str(self.E90mean) + ' kN/mm²')
            self.GmeanLabel.setText('Gmean: ' + str(self.Gmean) + ' kN/mm²')
            self.rkLabel.setText('rk: ' + str(self.rk) + ' kg/m³')
            self.rmeanLabel.setText('rmean: ' + str(self.rmean) + ' kg/m³')

            self.DimBoundaries(0)

    def selectedBeamStep(self):
        self.interaxis = self.BeamStepValue.value()
        self.InfluenceAreaValue.setValue(self.length*self.interaxis)
#        G2tmp = self.G2avr+(self.g2load*self.interaxis)
        G2tmp = self.G2avr+self.G2load
        self.G2LoadValue.setValue(G2tmp)

        self.DimBoundaries(0)

    def selectedInfluenceArea(self):
        A = self.InfluenceAreaValue.value()
        self.interaxis = A/self.length
        self.BeamStepValue.setValue(self.interaxis)
#        G2tmp = self.G2avr+(self.g2load*self.interaxis)
        G2tmp = self.G2avr+self.G2load
        self.G2LoadValue.setValue(G2tmp)

        self.DimBoundaries(0)

    def DimBoundaries(self, SelBeam):
        # if G1LoadValue != 0 and (not G1LoadInit or G1LoadInit == 0): 
        #      G1LoadInit=G1LoadValue
        # if G2LoadValue != 0 and (not G2LoadInit or G2LoadInit == 0):
        #      if G2LoadValue != self G2avr:
        #          G2LoadInit = G2LoadValue + self.G2avr
        # dimensional boundaries
        if self.WoodTypeValue.currentText() and self.WoodClassValue.currentText() and self.StrengthValue.currentText():
            for i in range(0,len(self.GammaMList[:])):
                for l in self.GammaMList[i][0].split():
                    if l.lower() in self.WoodTypeValue.currentText().lower():
                        self.GammaM = self.GammaMList[i][2]
                        self.fc0d = self.NTC2018Data.DesignRes(self.kmodPerm, self.fc0k, self.GammaM)
                        self.ft0d = self.NTC2018Data.DesignRes(self.kmodPerm, self.ft0k, self.GammaM)
                        self.fmd = self.NTC2018Data.DesignRes(self.kmodPerm, self.fmk, self.GammaM)
                        self.fvd = self.NTC2018Data.DesignRes(self.kmodPerm, self.fvk, self.GammaM)

                        self.NormalStressLabel.setText('Normal stress fc0d: ' + str(self.fc0d) + ' kN/mm²')
                        self.BendingLabel.setText('Bending fmd: ' + str(self.fmd) + ' kN/mm²')
                        self.ShearLabel.setText('Shear fvd: ' + str(self.fvd) + ' kN/mm²')

                        self.Fd = self.NTC2018Data.FundComb(self.G1LoadValue.value(), self.GammaList[1][4], self.G2LoadValue.value(), self.GammaList[2][4], self.qk, self.GammaList[3][4])
                        self.bmin, self.hmin = self.NTC2018Data.PreDim(self.Fd, self.BeamStepValue.value(), self.length, self.fmd, self.fvd)
                        self.beamminweight, self.beamminQ = self.NTC2018Data.BeamWeight(self.bmin, self.hmin, self.length, self.rmean) 

                        self.FundCombLabel.setText('Fundamental Combination: ' + str(round(self.Fd, 2)) + ' kN/m²')
                        self.WidthMinLabel.setText('Section width minimum: ' + str(round(self.bmin, 2)) + ' mm')
                        self.HeightMinLabel.setText('Section height minimum: ' + str(round(self.hmin, 2)) + ' mm')
                        self.BeamMinWeightLabel.setText('Minimum section weight: '  + str(round(self.beamminweight, 4)) + '  kN')

                        if SelBeam == 1 or self.FinalBeamDim == 1:
                            print('SelectedBeam if:', SelBeam, 'self.FinalBeamDim', self.FinalBeamDim)
                            Width = self.B
                            Height = self.H
                            Length = self.length
                            rhomean = self.rmean
                            self.FinalBeamDim = 1
                            print('W: ', Width, 'H: ', Height)
                            self.beamweight, self.beamQ = self.NTC2018Data.BeamWeight(Width, Height, Length, rhomean) 
                            self.BeamWeightLabel.setText('Selected section weight: '  + str(round(self.beamweight, 4)) + '  kN')
                            self.SelectedWidthLabel.setText('Selected width: '  + str(round(Width, 4)) + '  mm')
                            self.SelectedHeightLabel.setText('Selected height: '  + str(round(Height, 4)) + '  mm')
                            print('G1avr', self.G1avr, 'self.beamQ', self.beamQ)
                            G1tmp = round(self.beamQ + self.G1avr, 4)
                            if G1tmp != 0 and G1tmp != self.G1LoadValue.value():
                                self.G1LoadValue.setMinimum(G1tmp)
                                self.G1LoadValue.setValue(G1tmp)
                                print('self.FinalBeamDim:', self.FinalBeamDim, 'G1tmp:', G1tmp, 'self.G1LoadValue.value', self.G1LoadValue.value())
                            self.checkSLU(Width, Height)
#                            else:
#                                self.FinalBeamDim = 0
#                                print('self.FinalBeamDim:', self.FinalBeamDim, 'G1tmp:', G1tmp, 'self.G1LoadValue.value', self.G1LoadValue.value())
#                                return
                        elif SelBeam != 1 and self.FinalBeamDim != 1:
                            print('SelectedBeam else if:', SelBeam, 'self.FinalBeamDim', self.FinalBeamDim)
                            print('self.bmin', self.bmin, 'selW: ', self.selWidth, 'self.hmin', self.hmin, 'selH: ', self.selHeight)
                            if self.selWidth >= self.bmin and self.selHeight >= self.hmin and self.oldbeamweight != self.beamweight:
                                Width = self.selWidth
                                Height = self.selHeight
                                print('selW: ', self.selWidth, 'selH: ', self.selHeight)
                                self.beamweight, self.beamQ = self.NTC2018Data.BeamWeight(self.selWidth, self.selHeight, self.length, self.rmean) 
                                self.oldbeamweight = self.beamweight
                                self.BeamWeightLabel.setText('Selected section weight: '  + str(round(self.beamweight, 4)) + '  kN')
                                self.SelectedWidthLabel.setText('Selected width: '  + str(round(self.selWidth, 4)) + '  mm')
                                self.SelectedHeightLabel.setText('Selected height: '  + str(round(self.selHeight, 4)) + '  mm')
                                G1tmp = round(self.beamQ + self.G1avr, 4)
                                print('G1avr', self.G1avr, 'self.beamQ', self.beamQ)
                                if G1tmp != 0 and G1tmp != self.G1LoadValue.value():
                                    self.G1LoadValue.setMinimum(G1tmp)
                                    self.G1LoadValue.setValue(G1tmp)
                                if 0 < Width < float("inf") and 0 < Height < float("inf"):
                                    self.checkSLU(Width, Height)
                            elif self.selWidth >= self.bmin and self.selHeight >= self.hmin and self.oldbeamweight == self.beamweight:
                                self.checkSLU(self.selWidth, self.selHeight)
                            else:
                                print('else', 'G1avr', self.G1avr, 'self.beamminweight', self.beamminweight, 'self.beamweight', self.beamweight)
                                G1tmp = round(self.beamminQ + self.G1avr, 4)
                                print('G1tmp', G1tmp, 'self.G1LoadValue.value()', self.G1LoadValue.value())
                                if G1tmp != 0 and G1tmp != self.G1LoadValue.value():
                                    self.G1LoadValue.setMinimum(G1tmp)
                                    self.G1LoadValue.setValue(G1tmp)

            if SelBeam != 1 and self.FinalBeamDim != 1:
                print('DimBoundaries SelBeam', SelBeam, 'self.FinalBeamDim', self.FinalBeamDim)
                self.BeamComDimm()
            elif SelBeam != 1 and self.FinalBeamDim == 1:
                self.FinalBeamDim = 0
                print('DimBoundaries SelBeam', SelBeam, 'self.FinalBeamDim', self.FinalBeamDim)

    def BeamComDimm(self):
        print('BeamComDimm')
        self.DimCommValue.clear()
        for i in range(0,len(self.BeamDimList[:])):
                text = 'text'
                Length = self.length*1000 # m -> mm
                if (self.BeamDimList[i][0] >= self.bmin) and (self.BeamDimList[i][1] >= self.hmin) and (self.BeamDimList[i][2] >= Length):
                    text = str(self.BeamDimList[i][0]) + 'x' + str(self.BeamDimList[i][1]) + 'x' + str(self.BeamDimList[i][2])
                    self.DimCommValue.addItem(text)
                    if self.DimCommValue.count() == 1:
                        self.selWidth = self.BeamDimList[i][0]
                        self.selHeight = self.BeamDimList[i][1]
        text = 'Custom...'
        self.DimCommValue.addItem(text)
        if self.DimCommValue.count() == 1:
            self.DimCommXValue.show()
            self.DimCommYValue.show()
            self.DimCommXValue.setMinimum(self.bmin)
            self.DimCommYValue.setMinimum(self.hmin)
        elif self.DimCommValue.count() >= 1 and self.DimCommXValue.isVisibleTo(self.form) and self.DimCommYValue.isVisibleTo(self.form):
            self.DimCommXValue.hide()
            self.DimCommYValue.hide()

    def selectedDimComm(self):
        index = self.DimCommValue.currentIndex()
        IndexCount = self.DimCommValue.count() -1
        print(self.DimCommValue.currentText())
        if index == IndexCount:
            self.DimCommXValue.show()
            self.DimCommYValue.show()
            self.DimCommXValue.setMinimum(self.bmin)
            self.DimCommYValue.setMinimum(self.hmin)
        elif index != IndexCount:
            if self.DimCommXValue.isVisibleTo(self.form) and self.DimCommYValue.isVisibleTo(self.form):
                self.DimCommXValue.hide()
                self.DimCommYValue.hide()
            self.section = self.DimCommValue.currentText().split('x')
            self.B = float(self.section[0])
            self.H = float(self.section[1])

        self.DimBoundaries(1)

    def selectedDimCommXY(self):
        self.B = self.DimCommXValue.value()
        self.H = self.DimCommYValue.value()

        self.DimBoundaries(1)

    def checkSLU(self, Width, Height):
#        Width = self.B
#        Height = self.H
        if Width == 0 or Height == 0:
            return
        Length = self.length
        Moment = self.NTC2018Data.MomentEq(self.Fd, self.interaxis, Length, self.alpha)
        Shear = self.NTC2018Data.ShearForceEq(self.Fd, self.interaxis, Length, self.alpha)
        Deflection = self.NTC2018Data.DeflectionEq(self.Fd, self.interaxis, Width, Height, Length, self.alpha, self.E005)
        NormalStress = self.NTC2018Data.NormalStress(self.Fd, self.interaxis, Length, self.alpha, self.Hk)
        Wmax, Wmin = self.NTC2018Data.SectionModulus(Width, Height)

        if Wmax != 0:
            Check_fmd = self.NTC2018Data.Verify_Bending(Moment, Wmax, self.fmd)
            Check_fvd = self.NTC2018Data.Verify_Shear(Shear, Width, Height, self.fvd)
            Check_fx0d = self.NTC2018Data.Verify_NormalStress(NormalStress, Width, Height, self.fc0d, self.ft0d)
            Check_Deflection = self.NTC2018Data.Verify_Deflection(Deflection, Length)

            if Check_fmd and Check_fvd and Check_fx0d and Check_Deflection:
                print('Verified')
            else:
                print('Verification Fail')
                print('Check_fmd', Check_fmd, 'Check_fvd', Check_fvd, 'Check_fx0d', Check_fx0d, 'Check_Deflection', Check_Deflection)
                print('Moment', Moment, 'Shear', Shear, 'Deflection', Deflection, 'NormalStress', NormalStress, 'Wmax', Wmax)

    def Section(self, selection, Width, Height):
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

                section = FreeCAD.Draft.make_wire([p1, p2, p3, p4], closed=True)

                v = FreeCAD.Vector(x1,y1,z1).sub(FreeCAD.Vector(x2,y2,z2))
                r = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),v)
                pl = FreeCAD.Placement()
                pl.Rotation.Q = r.Q
                pl.Base = FreeCAD.Vector(x1,y1,z1)
                section.Placement = pl

    # Ok and Cancel buttons are created by default in FreeCAD Task Panels
    # What is done when we click on the ok button.
    def accept(self):
        WoodType = self.WoodTypeValue.currentText()
        WoodClass = self.WoodClassValue.currentText()
        WoodStrengthClass = self.StrengthValue.currentText()

        doc = FreeCAD.ActiveDocument
        #selection = FreeCADGui.Selection.getSelection()

        objmat = doc.addObject("Part::FeaturePython", "Material")

        Material(objmat, self.selection, WoodType, WoodClass, WoodStrengthClass, self.fmk, self.ft0k, self.ft90k, self.fc0k, self.fc90k, self.fvk, self.E0mean, self.E005, self.E90mean, self.Gmean, self.rk, self.rmean)
        ViewProviderMaterial(objmat.ViewObject)

        self.Section(self.selection, self.B, self.H)

        doc.recompute()
        FreeCADGui.Control.closeDialog() #close the dialog

    # What is done when we click on the cancel button.
    # commented because this is the default behaviour
    #def reject(self):
    #   FreeCADGui.Control.closeDialog()


    def getIcon(self):
        return """
/* XPM */
static char *sizing[] = {
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


class CommandSizing():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/sizing.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+S", # a default shortcut (optional)
                "MenuText": "sizing structure",
                "ToolTip" : "Sizing the structure"}
    
    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        doc = FreeCAD.ActiveDocument

        # what is done when the command is clicked
        # creates a panel with a dialog
        panel = Sizing(selection)
        # having a panel with a widget in self.form and the accept and 
        # reject functions (if needed), we can open it:
        FreeCADGui.Control.showDialog(panel)

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand('sizing', CommandSizing())
