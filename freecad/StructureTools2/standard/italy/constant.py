#import FreeCAD, App, FreeCADGui, Part, os, math
#from PySide import QtWidgets, QtCore, QtGui
#import subprocess
import os

ICONPATH = os.path.join(os.path.dirname(__file__), 'resources')

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Error icon
    msg_box.setWindowTitle('Error')
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

def set_type(s):
    # Takes a string, inferes the type and returns either a string, int or float.
    if isinstance(s, int) or isinstance(s, float):
        return s
    if s.isnumeric():
        return int(s)
    if s.count('.') == 1 and ''.join([c for c in s if c!='.']).isnumeric():
        return float(s)
    return s

class Constant:
    def Strength():
        # mapped list ['StrengthClass', fmk, ft0k, ft90k, fc0k, fc90k, fvk, E0mean, E005, E90mean, Gmean, rk, rmean]
        StrengthList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        StrengthList.append(list(map(set_type, ['C14', '14', '8', '0.4', '16', '2.0', '1.7', '7', '4.7', '0.23', '0.44', '290', '350'])))
        StrengthList.append(list(map(set_type, ['C16', '16', '10', '0.5', '17', '2.2', '1.8', '8', '5.4', '0.27', '0.50', '310', '370'])))
        StrengthList.append(list(map(set_type, ['C18', '18', '11', '0.5', '18', '2.2', '2.0', '9', '6.0', '0.30', '0.56', '320', '380'])))
        StrengthList.append(list(map(set_type, ['C20', '20', '12', '0.5', '19', '2.3', '2.2', '9.5', '6.4', '0.32', '0.59', '330', '390'])))
        StrengthList.append(list(map(set_type, ['C22', '22', '13', '0.5', '20', '2.4', '2.4', '10', '6.7', '0.33', '0.63', '340', '410'])))
        StrengthList.append(list(map(set_type, ['C24', '24', '14', '0.5', '21', '2.5', '2.5', '11', '7.4', '0.37', '0.69', '350', '420'])))
        StrengthList.append(list(map(set_type, ['C27', '27', '16', '0.6', '22', '2.6', '2.8', '11.5', '7.7', '0.38', '0.72', '370', '450'])))
        StrengthList.append(list(map(set_type, ['C30', '30', '18', '0.6', '23', '2.7', '3.0', '12', '8.0', '0.40', '0.75', '380', '460'])))
        StrengthList.append(list(map(set_type, ['C35', '35', '21', '0.6', '25', '2.8', '3.4', '13', '8.7', '0.43', '0.81', '400', '480'])))
        StrengthList.append(list(map(set_type, ['C40', '40', '24', '0.6', '26', '2.9', '3.8', '14', '9.4', '0.47', '0.88', '420', '500'])))
        StrengthList.append(list(map(set_type, ['C45', '45', '27', '0.6', '27', '3.1', '3.8', '15', '10.0', '0.50', '0.94', '440', '520'])))
        StrengthList.append(list(map(set_type, ['C50', '50', '30', '0.6', '29', '3.2', '3.8', '16', '10.7', '0.53', '1.00', '460', '550'])))
        StrengthList.append(list(map(set_type, ['D30', '30', '18', '0.6', '23', '8.0', '3.0', '10', '8.0', '0.64', '0.60', '530', '640'])))
        StrengthList.append(list(map(set_type, ['D35', '35', '21', '0.6', '25', '8.4', '3.4', '10', '8.7', '0.69', '0.65', '560', '670'])))
        StrengthList.append(list(map(set_type, ['D40', '40', '24', '0.6', '26', '8.8', '3.8', '11', '9.4', '0.75', '0.70', '590', '700'])))
        StrengthList.append(list(map(set_type, ['D50', '50', '30', '0.6', '29', '9.7', '4.6', '14', '11.8', '0.93', '0.88', '650', '780'])))
        StrengthList.append(list(map(set_type, ['D60', '60', '36', '0.6', '32', '10.5', '5.3', '17', '14.3', '1.13', '1.06', '700', '840'])))
        StrengthList.append(list(map(set_type, ['D70', '70', '42', '0.6', '34', '13.5', '6.0', '20', '16.8', '1.33', '1.25', '900', '1080'])))

        return StrengthList
