import FreeCAD, App, FreeCADGui, Part, os, math
from PySide import QtWidgets, QtCore, QtGui
from geographiclib.geodesic import Geodesic
import requests, json
import numpy
from pathlib import Path

from srtm import Srtm1HeightMapCollection

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
    if s.isnumeric():
        return int(s)
    if s.count('.') == 1 and ''.join([c for c in s if c!='.']).isnumeric():
        return float(s)
    return s


# function for return elevation from lat, long, based on python-srtm
# which in turn is based on Nasa SRTM1
def get_SRTM1_elevation(lat, long, api_key):
    print(lat, long, api_key)
    elevation = 9999
#    srtm1_data = Srtm1HeightMapCollection(Path=.)
#    srtm1_data.build_file_index()
#    elevation = srtm1_data.get_altitude(latitude=lat, longitude=long)
    return elevation

def get_elevation(lat, long):
    url = (f'https://api.open-elevation.com/api/v1/lookup?locations={lat},{long}')
    data = requests.get(url).json()  # json object, various ways you can extract value
    elevation = data['results'][0]['elevation']*1000
    return elevation

# function for return reverse geocoding from lat, long, based on nominatim.openstreetmap.org api
def get_location(lat, long):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36", 'Referer': 'https://none.net'}
    url = (f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={long}&zoom=18&format=json')
    data = requests.get(url, headers=headers).json()  # json object, various ways you can extract value
    town = data['address']['town']
    county = data['address']['county']
    country = data['address']['country']
    country_code = data['address']['country_code']
    return  town, county, country, country_code
    

class Project:
    def __init__(self, obj):
        self.center = ()
        self.NordWest = {}
        self.SouthEst = {}
        self.Cu = 0
        self.Vn = 0
        self.obj = obj
        self.obj.addProperty("App::PropertyString", "BuildingStandard", "Project", "Building standard")
        self.obj.addProperty("App::PropertyAngle", "Latitude", "Project", "Geographic latitude of building site").Latitude = 0
        self.obj.addProperty("App::PropertyAngle", "Longitude", "Project", "Geographic longitude of building site").Longitude = 0
        self.obj.addProperty("App::PropertyDistance", "Elevation", "Project", "Geographic elevation of building site").Elevation = 0
        self.obj.addProperty("App::PropertyString", "CountryCode", "Project", "Country Code").CountryCode = 'None'
        self.obj.addProperty("App::PropertyString", "Country", "Project", "Country").Country = 'None'
        self.obj.addProperty("App::PropertyString", "County", "Project", "County").County = 'None'
        self.obj.addProperty("App::PropertyString", "Town", "Project", "Town").Town = 'None'
        self.obj.addProperty("App::PropertyString", "NominalLife", "Project", "Nominal life time of building").NominalLife = 'None'
        self.obj.addProperty("App::PropertyInteger", "Vn", "Project", "Nominal life time of building").Vn = self.Vn
        self.obj.addProperty("App::PropertyString", "UseClass", "Project", "Use class of building").UseClass = 'None'
        self.obj.addProperty("App::PropertyFloat", "Cu", "Project", "Use class coefficient of building").Cu = self.Cu
        self.form = [QtGui.QDialog(), QtGui.QDialog(), QtGui.QDialog()]
        self.StandardSelection()

    def StandardSelection(self):
        # Building Standard Selection QDialog
        layoutStd = QtGui.QVBoxLayout()
        self.form[0].setWindowTitle('Building Standard')
        self.StandardValue = QtGui.QComboBox()
        self.StandardValue.addItem('')
        self.StandardValue.addItem('Italy: ntc2018')
        self.StandardValue.activated.connect(self.selectedStandard)
        #self.StandardValue.currentIndexChanged.connect(self.selectedStandard)
        layoutStd.addWidget(self.StandardValue)
        self.form[0].setLayout(layoutStd)

    def selectedStandard(self):
        index = self.StandardValue.currentIndex()
        if index == 1:
            self.GeoMode()
            self.ProjectParam()
        #elif index == 2:
        # Entry for other standard

    def GeoMode(self):
        self.LayoutGeo = QtGui.QVBoxLayout()
        self.form[1].setWindowTitle('GeoLocation')
        self.GeoModeLabel = QtGui.QLabel('Select geolocation mode:')

        self.formGeoMode = QtGui.QDialog()
        self.LayoutGeoMode = QtGui.QHBoxLayout()
        self.OpenTopographyRadioButton = QtGui.QRadioButton('OpenTopography')
        self.OpenTopographyRadioButton.toggled.connect(self.OpenTopography)
        self.ShapeFileRadioButton = QtGui.QRadioButton('Shapefile')
        self.ShapeFileRadioButton.toggled.connect(self.ShapeFile)

        self.formShapeFile = QtGui.QDialog()
        self.LayoutShapeFile = QtGui.QVBoxLayout()
        self.ShapeFileLabel = QtGui.QLabel('Select Shapefile:')

        self.formShapeFileSelect = QtGui.QDialog()
        self.LayoutShapeFileSelect = QtGui.QHBoxLayout()
        self.ShapeFileValue = QtGui.QLineEdit()
        self.ShapeFileValue.setClearButtonEnabled(True)
        self.ShapeFileButton = QtGui.QPushButton('Browse')
        self.ShapeFileButton.clicked.connect(self.ShapeFileOpen)

        self.LayoutShapeFileSelect.addWidget(self.ShapeFileValue)
        self.LayoutShapeFileSelect.addWidget(self.ShapeFileButton)
        self.formShapeFileSelect.setLayout(self.LayoutShapeFileSelect)

        self.LayoutShapeFile.addWidget(self.ShapeFileLabel)
        self.LayoutShapeFile.addWidget(self.formShapeFileSelect)
        self.formShapeFile.setLayout(self.LayoutShapeFile)

        self.formShapeFile.hide()

        self.formOpenTopography = QtGui.QDialog()
        self.LayoutOpenTopography = QtGui.QVBoxLayout()
        self.LocationLabel = QtGui.QLabel('Location [EPSG:4326]:')
        self.LatitudeValue = QtGui.QDoubleSpinBox()
        self.LongitudeValue = QtGui.QDoubleSpinBox()
        self.LandAreaRadiusValue = QtGui.QDoubleSpinBox()
        self.LatitudeValue.setPrefix('Latitude: ')
        self.LongitudeValue.setPrefix('Longitude: ')
        self.LandAreaRadiusValue.setPrefix("Land's area radius: ")
        self.LatitudeValue.setSuffix('deg')
        self.LongitudeValue.setSuffix('deg')
        self.LandAreaRadiusValue.setSuffix('m')
        self.LatitudeValue.setDecimals(6)
        self.LongitudeValue.setDecimals(6)
        self.LandAreaRadiusValue.setDecimals(0)
        self.LatitudeValue.setMinimum(-90.000000)
        self.LatitudeValue.setMaximum(90.000000)
        self.LongitudeValue.setMinimum(-180.000000)
        self.LongitudeValue.setMaximum(180.000000)
        self.LandAreaRadiusValue.setMinimum(0)
        self.LandAreaRadiusValue.valueChanged.connect(self.calcArea)
        self.LandAreaValueLabel = QtGui.QLabel('0 m²')
        self.OpenTopographyLabel = QtGui.QLabel('OpenTopography API key:')
        self.OpenTopographyValue = QtGui.QLineEdit()
        self.OpenTopographyValue.setClearButtonEnabled(True)

        self.LayoutOpenTopography.addWidget(self.LocationLabel)
        self.LayoutOpenTopography.addWidget(self.LatitudeValue)
        self.LayoutOpenTopography.addWidget(self.LongitudeValue)
        self.LayoutOpenTopography.addWidget(self.LandAreaRadiusValue)
        self.LayoutOpenTopography.addWidget(self.LandAreaValueLabel)
        self.LayoutOpenTopography.addWidget(self.OpenTopographyLabel)
        self.LayoutOpenTopography.addWidget(self.OpenTopographyValue)

        self.formOpenTopography.hide()
        self.formOpenTopography.setLayout(self.LayoutOpenTopography)

        self.LayoutGeoMode.addWidget(self.OpenTopographyRadioButton)
        self.LayoutGeoMode.addWidget(self.ShapeFileRadioButton)
        self.formGeoMode.setLayout(self.LayoutGeoMode)

        self.LayoutGeo.addWidget(self.GeoModeLabel)
        self.LayoutGeo.addWidget(self.formGeoMode)
        self.LayoutGeo.addWidget(self.formShapeFile)
        self.LayoutGeo.addWidget(self.formOpenTopography)

        self.form[1].setLayout(self.LayoutGeo)

    def ShapeFileOpen(self):
        if self.ShapeFileValue.text():
            path = Path(self.ShapeFileValue.text()).as_posix()
        else:
            path = Path.home().as_posix()
        filename, ok = QtGui.QFileDialog.getOpenFileName(None, "Select ShapeFile", path, "ShapeFile (*.shp)")
        print(filename)
        if filename:
            self.ShapeFileValue.setText(str(filename))
            self.selectedShapeFile(filename)

    def selectedShapeFile(self, filename):
        print(filename)
        self.obj.Latitude = '45.52868 deg'
        self.obj.Longitude = '9.04425 deg'

    def ShapeFile(self):
        self.formOpenTopography.hide()
        self.formShapeFile.show()

    def OpenTopography(self):
        self.formShapeFile.hide()
        self.formOpenTopography.show()

    def calcArea(self):
        lat = str(self.LatitudeValue.value()).strip(' deg')
        long = str(self.LongitudeValue.value()).strip(' deg')
        self.center = (float(lat),float(long))
        dist = self.LandAreaRadiusValue()/1000
        self.NordWest = Geodesic.WGS84.Direct(self.center[0],self.center[1],315,dist)
        self.SouthEst = Geodesic.WGS84.Direct(self.center[0],self.center[1],45,dist)
        latNW, longNW = (float(format(self.NordWest['lat2'])),float(format(self.NordWest['lon2'])))
        latSE, longSE = (format(SouthEst['lat2'])),float(format(SouthEst['lon2'])))
        LandArea = Geodesic.WGS84.Inverse(latNW, longNW, latSE, longSE, Geodesic.AREA)
        self.LandAreaValueLabel.setText(LandArea,'m²')
        
    def ProjectParam(self):
        # ntc2018 Project Parameter QDialog
        self.layoutProj = QtGui.QVBoxLayout()
        self.form[2].setWindowTitle('Project Parameter')

        # mapped list ['description', Vn]
        self.NomLifeList = [list(map(set_type, ['', '0']))]
        self.NomLifeList.append(list(map(set_type, ['Temporary and provisional buildings', '10'])))
        self.NomLifeList.append(list(map(set_type, ['Buildings with ordinary performance levels', '50'])))
        self.NomLifeList.append(list(map(set_type, ['Buildings with high performance levels', '100'])))

        self.NominalLifeLabel = QtGui.QLabel('Nominal life time Vn [ntc2018 Tab. 2.4.I]:')
        self.NominalLifeValue = QtGui.QComboBox()
        for i in range(0,len(self.NomLifeList[:])):
            self.NominalLifeValue.addItem(self.NomLifeList[i][0])
        self.NominalLifeValue.activated.connect(self.selectedNomLife)
        #self.NominalLifeValue.currentIndexChanged.connect(self.selectedNomLife)
        self.VnLabel = QtGui.QLabel('Vn: 0 years')

        # mapped list ['description', Cu]
        self.UseClassList = [list(map(set_type, ['', '0.0']))]
        self.UseClassList.append(list(map(set_type, ['Class I: Buildings with only occasional presence of people, agricultural buildings', '0.7'])))
        self.UseClassList.append(list(map(set_type, ['Class II: Buildings whose use involves normal crowding', '1.0'])))
        self.UseClassList.append(list(map(set_type, ['Class III: Buildings whose use involves significant crowding', '1.5'])))
        self.UseClassList.append(list(map(set_type, ['Class IV: Buildings with important public or strategic functions', '2.0'])))

        self.UseClassLabel = QtGui.QLabel('Building use class Cu [ntc2018 Ch. 2.4.2]:')
        self.UseClassValue = QtGui.QComboBox()
        for i in range(0,len(self.UseClassList[:])):
            self.UseClassValue.addItem(self.UseClassList[i][0])
        self.UseClassValue.activated.connect(self.selectedUseClass)
        #self.UseClassValue.currentIndexChanged.connect(self.selectedUseClass)
        self.CuValue = QtGui.QDoubleSpinBox()
        self.CuValue.setValue(0.0)
        self.CuValue.setPrefix('Cu: ')

        self.layoutProj.addWidget(self.NominalLifeLabel)
        self.layoutProj.addWidget(self.NominalLifeValue)
        self.layoutProj.addWidget(self.VnLabel)
        self.layoutProj.addWidget(self.UseClassLabel)
        self.layoutProj.addWidget(self.UseClassValue)
        self.layoutProj.addWidget(self.CuValue)
        self.form[2].setLayout(self.layoutProj)

    def selectedNomLife(self):
        index = self.NominalLifeValue.currentIndex()
        self.Vn = self.NomLifeList[index][1]
        self.VnLabel.setText('Vn: ' + str(self.Vn) + ' years')
        
    def selectedUseClass(self):
        index = self.UseClassValue.currentIndex()
        self.Cu = self.UseClassList[index][1]
        self.CuValue.setMinimum(self.Cu)
        self.CuValue.setValue(self.Cu)

    def surfacePoint(self, center, lats, longs):
        centerZ = get_elevation(center[0],center[1])
        r = []
        v = []
        for lat in lats:
            for long in longs:
                dist_z = get_elevation(float(lat), float(long)) - centerZ
                dist_x = Geodesic.WGS84.Inverse(float(lat),float(long),center[0],float(long))
                dist_y = Geodesic.WGS84.Inverse(float(lat),float(long),float(lat),center[1])
                sign_x = float(format(dist_x['lat1']))-float(format(dist_x['lat2']))
                sign_y = float(format(dist_y['lon1']))-float(format(dist_y['lon2']))
                x = float(format(dist_x['s12']))
                y = float(format(dist_y['s12']))
                if sign_x < 0:
                    x = -x
                if sign_y < 0:
                    y = -y
                z = dist_z/1000

                if len(r) != 0:
                    if x != r[len(r[:])-1][0]:
                        v.append(r)
                        r = [FreeCAD.Vector(x,y,z)]
                    else:
                        r.append(FreeCAD.Vector(x,y,z))
                else:
                    r.append(FreeCAD.Vector(x,y,z))
        return v

    # Ok and Cancel buttons are created by default in FreeCAD Task Panels
    # What is done when we click on the ok button.
    def accept(self):
        self.obj.BuildingStandard = self.StandardValue.currentText()
        if not self.obj.Latitude and not self.obj.Longitude:
            self.obj.Latitude = self.LatitudeValue.value()
            self.obj.Longitude = self.LongitudeValue.value()
        print)self.obj.Latitude,self.obj.Longitude)

        lats = numpy.arange(float(format(self.NordWest['lat2'])),float(format(self.SouthEst['lat2'])),0.00025)
        longs = numpy.arange(float(format(self.NordWest['lon2'])),float(format(self.SouthEst['lon2'])),0.00025)

        vectors = self.surfacePoint(self.center,lats,longs)

        api_key = self.OpenTopographyValue.text()
        if api_key:
            self.obj.Elevation = get_SRTM1_elevation(lat, long, api_key)
        else:
            self.obj.Elevation = get_elevation(lat, long)

        self.obj.NominalLife = self.NominalLifeValue.currentText()
        self.obj.Vn = self.Vn
        self.obj.UseClass = self.UseClassValue.currentText()
        self.obj.Cu = self.Cu
        self.obj.setEditorMode("BuildingStandard",1) # readOnly
        self.obj.setEditorMode("Latitude",1) # readOnly
        self.obj.setEditorMode("Longitude",1) # readOnly
        self.obj.setEditorMode("Elevation",1) # readOnly
        self.obj.setEditorMode("NominalLife",1) # readOnly
        self.obj.setEditorMode("Vn",1) # readOnly
        self.obj.setEditorMode("UseClass",1) # readOnly
        self.obj.setEditorMode("Cu",1) # readOnly

        self.obj.Town, self.obj.County, self.obj.Country, self.obj.CountryCode = get_location(lat, long)

        FreeCADGui.Control.closeDialog() #close the dialog

    # What is done when we click on the cancel button.
    # commented because this is the default behaviour
    #def reject(self):
    #   FreeCADGui.Control.closeDialog()

class ViewProviderProject:
    def __init__(self, obj):
        obj.Proxy = self

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


class CommandProject():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/sizing.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+S", # a default shortcut (optional)
                "MenuText": "Define a new building project for structure sizing",
                "ToolTip" : "Define a new building project for structure sizing"}
    
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::GeometryPython","Project")
        obj.addExtension("App::GeoFeatureGroupExtensionPython")
        obj.ViewObject.addExtension("Gui::ViewProviderGeoFeatureGroupExtensionPython")

        # what is done when the command is clicked
        # creates a panel with a dialog
        objSuport = Project(obj)
        ViewProviderProject(obj.ViewObject)

        # having a panel with a widget in self.form and the accept and 
        # reject functions (if needed), we can open it:
        FreeCADGui.Control.showDialog(objSuport)

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand('project', CommandProject())
