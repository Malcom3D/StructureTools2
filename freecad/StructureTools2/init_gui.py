import os
import FreeCADGui as Gui
import FreeCAD as App
import subprocess


translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()



from .Pynite_main.FEModel3D import FEModel3D

# from .Pynite_main.FEModel3D import FEModel3D
# try:
# 	from Pynite import FEModel3D
# except:
# 	print('Instalando dependencias')
# 	subprocess.check_call(["pip", "install", "PyniteFEA"])

class StructureTools2(Gui.Workbench):
	"""
	class which gets initiated at startup of the gui
	"""
	MenuText = translate("Workbench", "StructureTools2")
	ToolTip = translate("Workbench", "a simple StructureTools2")
	Icon = os.path.join(ICONPATH, "icone.svg")
	toolbox = []

	def GetClassName(self):
		return "Gui::PythonWorkbench"

	def Initialize(self):
		"""
		This function is called at the first activation of the workbench.
		here is the place to import all the commands
		"""
		from freecad.StructureTools2 import load_distributed
		from freecad.StructureTools2 import load_nodal
		from freecad.StructureTools2 import suport
		from freecad.StructureTools2 import section
#		from freecad.StructureTools2 import material
		from freecad.StructureTools2 import member
		from freecad.StructureTools2 import project
		from freecad.StructureTools2 import sizing
		from freecad.StructureTools2 import calc
		from freecad.StructureTools2 import diagram

		
		import DraftTools, SketcherGui
		# NOTE: Context for this commands must be "Workbench"
		self.appendToolbar('DraftDraw', ["Sketcher_NewSketch","Draft_Line", "Draft_Wire", "Draft_ArcTools", "Draft_BSpline", "Draft_Dimension"])
		self.appendToolbar('DraftEdit', ["Draft_Move", "Draft_Rotate", "Draft_Clone", "Draft_Offset", "Draft_Trimex", "Draft_Join", "Draft_Split","Draft_Stretch","Draft_Draft2Sketch"])
		self.appendToolbar('DraftSnap', ["Draft_Snap_Lock", "Draft_Snap_Endpoint", "Draft_Snap_Midpoint", "Draft_Snap_Center", "Draft_Snap_Angle", "Draft_Snap_Intersection", "Draft_Snap_Perpendicular", "Draft_Snap_Extension", "Draft_Snap_Parallel", "Draft_Snap_Special", "Draft_Snap_Near", "Draft_Snap_Ortho", "Draft_Snap_Grid", "Draft_Snap_WorkingPlane", "Draft_Snap_Dimensions", "Draft_ToggleGrid"])
		self.appendToolbar('DraftTools', ["Draft_SelectPlane", "Draft_SetStyle"])

		self.appendToolbar('StructureLoad', ["load_distributed","load_nodal"])
		self.appendToolbar('StructureProject', ["project"])
		self.appendToolbar('StructureTools2', ["member", "suport", "section"])
		self.appendToolbar('StructureResults', ["sizing","calc","diagram"])
		self.appendMenu('StructureTools2',["load_distributed", "load_nodal", "member" ,"suport", "section", "project", "sizing", "calc", "diagram"])

	def Activated(self):
		'''
		code which should be computed when a user switch to this workbench
		'''
		

		App.Console.PrintMessage(translate(
			"Log",
			"Workbench StructureTools2 activated.") + "\n")

	def Deactivated(self):
		'''
		code which should be computed when this workbench is deactivated
		'''
		App.Console.PrintMessage(translate(
			"Log",
			"Workbench StructureTools2 de-activated.") + "\n")


Gui.addWorkbench(StructureTools2())
