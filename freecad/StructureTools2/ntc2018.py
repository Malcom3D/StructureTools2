import FreeCAD, App, FreeCADGui, Part, os, math
from PySide import QtWidgets, QtCore, QtGui

class NTC2018:
    def __init__(self, form, Qavr):
        super().__init__()
        self.form = form
        self.Qavr = Qavr
#        self.StandardSelection()

    def StandardSelection(self):
        # Building Standard Selection QDialog
        layoutStd = QtGui.QVBoxLayout()
        self.form[0].setWindowTitle('Building Standard')
        self.StandardValue = QtGui.QComboBox()
        self.StandardValue.addItem('')
        self.StandardValue.addItem('Italy: ntc2018')
        #self.StandardValue.activated.connect(self.selectedStandard())
        self.StandardValue.currentIndexChanged.connect(self.selectedStandard)
        layoutStd.addWidget(self.StandardValue)
        self.form[0].setLayout(layoutStd)

    def selectedStandard(self):
        print('self.selectedStandard', self.StandardValue.currentIndex())
        if self.StandardValue.currentIndex() == 1:
            print('index1 self.LoadParam')
            self.LoadParam()
        #else:

    def LoadParam(self):
        # ntc2018 parameter QDialog
        self.form[1].setWindowTitle('ntc2018')
        layout = QtGui.QVBoxLayout()
        # Structural Load G1 [ntc2018 Tab. 3.1.I]
        self.G1LoadLabel = QtGui.QLabel('Structural load G1 [ntc2018 Tab. 3.1.I]')
        self.G1LoadValue = QtGui.QDoubleSpinBox()
        self.G1LoadValue.setMaximum(99999999999999999999999999.99)
        if self.Qavr:
            self.G1LoadValue.setValue(self.Qavr)
            self.G1LoadValue.setMinimum(self.Qavr)
        else:
            self.G1LoadValue.setValue(0)
        self.G1LoadValue.setSuffix(' kN/m²')

        # Non Structural Load G2 [ntc2018 3.1.3]
        self.G2LoadLabel = QtGui.QLabel('Non structural load G2 [ntc2018 3.1.3]')
        self.G2LoadValue = QtGui.QDoubleSpinBox()
        self.G2LoadValue.setValue(0)
        self.G2LoadValue.setSuffix(' kN/m²')

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

        self.Q1LoadLabel = QtGui.QLabel('Overloads by intended use Q1 [ntc2018 Tab. 3.1.II]')
        self.Q1LoadValue = QtGui.QComboBox()
        for i in range(0,len(self.Q1mapList[:])):
            self.Q1LoadValue.addItem(self.Q1mapList[i][0])
        self.Q1LoadValue.activated.connect(self.q1load)

        self.qkLoadLabel = QtGui.QLabel('qk: 0 kN/m²')
        self.QkLoadLabel = QtGui.QLabel('Qk: 0 kN')
        self.HkLoadLabel = QtGui.QLabel('Hk: 0 kN/m')

        self.MaterialLabel = QtGui.QLabel('Material')
        self.MaterialValue = QtGui.QComboBox()
        self.MaterialValue.addItem('')
        self.MaterialValue.addItem('Wood [UNI EN338 pag.254]')
        self.MaterialValue.addItem('Reinforced concrete')
        self.MaterialValue.addItem('Steel')
        self.MaterialValue.activated.connect(self.selectedMaterial)

        layout.addWidget(self.G1LoadLabel)
        layout.addWidget(self.G1LoadValue)
        layout.addWidget(self.G2LoadLabel)
        layout.addWidget(self.G2LoadValue)
        layout.addWidget(self.Q1LoadLabel)
        layout.addWidget(self.Q1LoadValue)
        layout.addWidget(self.qkLoadLabel)
        layout.addWidget(self.QkLoadLabel)
        layout.addWidget(self.HkLoadLabel)
        layout.addWidget(self.MaterialLabel)
        layout.addWidget(self.MaterialValue)

        self.form[1].setLayout(layout)

    def q1load(self, index):
        self.qk = self.Q1mapList[index][1]
        self.Qk = self.Q1mapList[index][2]
        self.Hk = self.Q1mapList[index][3]
        self.qkLoadLabel.setText('qk: ' + str(self.qk) + ' kN/m²')
        self.QkLoadLabel.setText('Qk: ' + str(self.Qk) + ' kN')
        self.HkLoadLabel.setText('Hk: ' + str(self.Hk) + ' kN/m')

    def selectedMaterial(self, index):
        if index == 1:
            self.MaterialParam()
#        else:

    def MaterialParam(self):
        # Material parameter
        layoutMaterial = QtGui.QVBoxLayout()

        # mapped list ['StrengthClass', fmk, ft0k, ft90k, fc0k, fc90k, fvk, E0mean, E005, E90mean, Gmean, rk, rmean]
        self.StrengthList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        self.StrengthList.append(list(map(set_type, ['C14', '14', '8', '0.4', '16', '2.0', '1.7', '7', '4.7', '0.23', '0.44', '290', '350'])))
        self.StrengthList.append(list(map(set_type, ['C16', '16', '10', '0.5', '17', '2.2', '1.8', '8', '5.4', '0.27', '0.50', '310', '370'])))
        self.StrengthList.append(list(map(set_type, ['C18', '18', '11', '0.5', '18', '2.2', '2.0', '9', '6.0', '0.30', '0.56', '320', '380'])))
        self.StrengthList.append(list(map(set_type, ['C20', '20', '12', '0.5', '19', '2.3', '2.2', '9.5', '6.4', '0.32', '0.59', '330', '390'])))
        self.StrengthList.append(list(map(set_type, ['C22', '22', '13', '0.5', '20', '2.4', '2.4', '10', '6.7', '0.33', '0.63', '340', '410'])))
        self.StrengthList.append(list(map(set_type, ['C24', '24', '14', '0.5', '21', '2.5', '2.5', '11', '7.4', '0.37', '0.69', '350', '420'])))
        self.StrengthList.append(list(map(set_type, ['C27', '27', '16', '0.6', '22', '2.6', '2.8', '11.5', '7.7', '0.38', '0.72', '370', '450'])))
        self.StrengthList.append(list(map(set_type, ['C30', '30', '18', '0.6', '23', '2.7', '3.0', '12', '8.0', '0.40', '0.75', '380', '460'])))
        self.StrengthList.append(list(map(set_type, ['C35', '35', '21', '0.6', '25', '2.8', '3.4', '13', '8.7', '0.43', '0.81', '400', '480'])))
        self.StrengthList.append(list(map(set_type, ['C40', '40', '24', '0.6', '26', '2.9', '3.8', '14', '9.4', '0.47', '0.88', '420', '500'])))
        self.StrengthList.append(list(map(set_type, ['C45', '45', '27', '0.6', '27', '3.1', '3.8', '15', '10.0', '0.50', '0.94', '440', '520'])))
        self.StrengthList.append(list(map(set_type, ['C50', '50', '30', '0.6', '29', '3.2', '3.8', '16', '10.7', '0.53', '1.00', '460', '550'])))
        self.StrengthList.append(list(map(set_type, ['D30', '30', '18', '0.6', '23', '8.0', '3.0', '10', '8.0', '0.64', '0.60', '530', '640'])))
        self.StrengthList.append(list(map(set_type, ['D35', '35', '21', '0.6', '25', '8.4', '3.4', '10', '8.7', '0.69', '0.65', '560', '670'])))
        self.StrengthList.append(list(map(set_type, ['D40', '40', '24', '0.6', '26', '8.8', '3.8', '11', '9.4', '0.75', '0.70', '590', '700'])))
        self.StrengthList.append(list(map(set_type, ['D50', '50', '30', '0.6', '29', '9.7', '4.6', '14', '11.8', '0.93', '0.88', '650', '780'])))
        self.StrengthList.append(list(map(set_type, ['D60', '60', '36', '0.6', '32', '10.5', '5.3', '17', '14.3', '1.13', '1.06', '700', '840'])))
        self.StrengthList.append(list(map(set_type, ['D70', '70', '42', '0.6', '34', '13.5', '6.0', '20', '16.8', '1.33', '1.25', '900', '1080'])))

        self.StrengthLabel = QtGui.QLabel('Strength class')
        self.StrengthValue = QtGui.QComboBox()
        for i in range(0,len(self.StrengthList[:])):
            self.StrengthValue.addItem(self.StrengthList[i][0])
        self.StrengthValue.activated.connect(self.selectedStrength)

        layoutMaterial.addWidget(self.StrengthLabel)
        layoutMaterial.addWidget(self.StrengthValue)

        self.form[2].setLayout(layoutMaterial)
        self.form[2].setWindowTitle('Material parameter')

    def selectedStrength(self, index):
        if index == 1:
            print("Selected Strength: ", self.StrengthValue.currentText())
