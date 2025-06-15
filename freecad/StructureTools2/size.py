import FreeCAD, App, FreeCADGui, Part, os, math
from PySide import QtWidgets
import subprocess

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

from sympy import *

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Error icon
    msg_box.setWindowTitle("Error")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class Size:
	def __init__(self, obj, elements):
		obj.Proxy = self
		obj.addProperty("App::PropertyLinkList", "ListElements", "Size", "elements for analysis").ListElements = elements
		
		obj.addProperty("App::PropertyString", "LengthUnit", "Calc", "set the length unit for calculation").LengthUnit = 'm'
		obj.addProperty("App::PropertyString", "ForceUnit", "Calc", "set the length unit for calculation").ForceUnit = 'kN'

		obj.addProperty("App::PropertyStringList", "NameMembers", "Calc", "name of structure members")
		obj.addProperty("App::PropertyVectorList", "Nodes", "Calc", "Nodes")
		obj.addProperty("App::PropertyBool", "selfWeight", "Calc", "Consider self weight").selfWeight = False

		obj.addProperty("App::PropertyStringList", "MomentY", "ResultMoment", "moment at local Y")
		obj.addProperty("App::PropertyStringList", "MomentZ", "ResultMoment", "moment at local Z")
		obj.addProperty("App::PropertyFloatList", "MinMomentY", "ResultMoment", "minimum moment in Y")
		obj.addProperty("App::PropertyFloatList", "MinMomentZ", "ResultMoment", "minimum moment in Z")
		obj.addProperty("App::PropertyFloatList", "MaxMomentY", "ResultMoment", "maximum moment in Y")
		obj.addProperty("App::PropertyFloatList", "MaxMomentZ", "ResultMoment", "maximum moment in Z")
		obj.addProperty("App::PropertyInteger", "NumPointsMoment", "NumPoints", "Graphics precision").NumPointsMoment = 5

		obj.addProperty("App::PropertyStringList", "AxialForce", "ResultAxial", "Axial Force")
		obj.addProperty("App::PropertyInteger", "NumPointsAxial", "NumPoints", "Graphics precision").NumPointsAxial = 3
		
		obj.addProperty("App::PropertyStringList", "Torque", "ResultTorque", "torque on element")
		obj.addProperty("App::PropertyFloatList", "MinTorque", "ResultTorque", "minimum torque")
		obj.addProperty("App::PropertyFloatList", "MaxTorque", "ResultTorque", "maximum torque")
		obj.addProperty("App::PropertyInteger", "NumPointsTorque", "NumPoints", "Graphics precision").NumPointsTorque = 3
		
		obj.addProperty("App::PropertyStringList", "ShearY", "ResultShear", "shear on Y axis")
		obj.addProperty("App::PropertyFloatList", "MinShearY", "ResultShear", "minimum shear on Y axis")
		obj.addProperty("App::PropertyFloatList", "MaxShearY", "ResultShear", "maximum shear on Y axis")
		obj.addProperty("App::PropertyStringList", "ShearZ", "ResultShear", "shear on Z axis")
		obj.addProperty("App::PropertyFloatList", "MinShearZ", "ResultShear", "minimum shear on Z axis")
		obj.addProperty("App::PropertyFloatList", "MaxShearZ", "ResultShear", "maximum shear on Z axis")
		obj.addProperty("App::PropertyInteger", "NumPointsShear", "NumPoints", "Graphics precision").NumPointsShear = 4

		obj.addProperty("App::PropertyStringList", "DeflectionY", "ResultDeflection", "deflection on Y axis")
		obj.addProperty("App::PropertyFloatList", "MinDeflectionY", "ResultDeflection", "minimum deflection on Y axis")
		obj.addProperty("App::PropertyFloatList", "MaxDeflectionY", "ResultDeflection", "maximum deflection on Y axis")
		obj.addProperty("App::PropertyStringList", "DeflectionZ", "ResultDeflection", "deflection on Z axis")
		obj.addProperty("App::PropertyFloatList", "MinDeflectionZ", "ResultDeflection", "minimum deflection on Z axis")
		obj.addProperty("App::PropertyFloatList", "MaxDeflectionZ", "ResultDeflection", "maximum deflection on Z axis")
		obj.addProperty("App::PropertyInteger", "NumPointsDeflection", "NumPoints", "Graphics precision").NumPointsDeflection = 4


        #  Maps the structure nodes, (inverts the y and z axis to adapt to the override coordinates)
	def mapNodes(self, elements, unitLength):	
                # Scans all line elements and adds their vertices to the nodes table
		listNodes = []
		for element in elements:
			for edge in element.Shape.Edges:
				for vertex in edge.Vertexes:
					node = [round(float(FreeCAD.Units.Quantity(vertex.Point.x,'mm').getValueAs(unitLength)), 2), round(float(FreeCAD.Units.Quantity(vertex.Point.z,'mm').getValueAs(unitLength)),2), round(float(FreeCAD.Units.Quantity(vertex.Point.y,'mm').getValueAs(unitLength)),2)]
					if not node in listNodes:
						listNodes.append(node)

		return listNodes

	# suppresses the members of the structure
	def mapMembers(self, elements, listNodes, unitLength):
		listMembers = {}
		for element in elements:
			for i, edge in enumerate(element.Shape.Edges):
				listIndexVertex = []
				for vertex in edge.Vertexes:
					node = [round(float(FreeCAD.Units.Quantity(vertex.Point.x,'mm').getValueAs(unitLength)), 2), round(float(FreeCAD.Units.Quantity(vertex.Point.z,'mm').getValueAs(unitLength)),2), round(float(FreeCAD.Units.Quantity(vertex.Point.y,'mm').getValueAs(unitLength)),2)]
					index = listNodes.index(node)
					listIndexVertex.append(index)

				# validates whether the first node is more self than the second node, if so inverts the nodes of the member (necessary to keep the diagrams facing the correct position)
				n1 = listIndexVertex[0]
				n2 = listIndexVertex[1]
				if listNodes[n1][1] > listNodes[n2][1]:
					aux = n1
					n1 = n2
					n2 = aux
				listMembers[element.Name + '_' + str(i)] = {
					'nodes': [str(n1), str(n2)],
					'material': element.MaterialMember.Name,
					'section': element.SectionMember.Name,
					'trussMember': element.TrussMember
					}
		
		return listMembers

	# Creates nodes in the solver model
	def setNodes(self, model, nodes_map):
		for i, node in enumerate(nodes_map):
			model.add_node(str(i), node[0], node[1], node[2])
		
		return model

	# Creates nodes in the solver model
	def setMembers(self, model, members_map,selfWeight):
		for memberName in list(members_map):			
			model.add_member(memberName, members_map[memberName]['nodes'][0] , members_map[memberName]['nodes'][1], members_map[memberName]['material'], members_map[memberName]['section'])
			
			# considers the self-weight on the bar elements
			if selfWeight : model.add_member_self_weight('FY', -1) 

			# frees the rotations at the ends of the element in order to emulate the behavior of truss bars
			if members_map[memberName]['trussMember']: model.def_releases(memberName, Dxi=False, Dyi=False, Dzi=False, Rxi=False, Ryi=True, Rzi=True, Dxj=False, Dyj=False, Dzj=False, Rxj=False, Ryj=True, Rzj=True)
		
		return model

	# Creates the loads
	def setLoads(self, model, loads, nodes_map, unitForce, unitLength):
		pass
		for load in loads:

			match load.GlobalDirection:
				case '+X':
					axis = 'FX'
					direction = 1

				case '-X':
					axis = 'FX'
					direction = -1

				case '+Y':
					axis = 'FZ'
					direction = 1

				case '-Y':
					axis = 'FZ'
					direction = -1

				case '+Z':
					axis = 'FY'
					direction = 1

				case '-Z':
					axis = 'FY'
					direction = -1

			# Validate if the load is distributed
			if 'Edge' in load.ObjectBase[0][1][0]:
				initial = float(load.InitialLoading.getValueAs(unitForce))
				final = float(load.FinalLoading.getValueAs(unitForce))

				subname = int(load.ObjectBase[0][1][0].split('Edge')[1]) - 1
				name = load.ObjectBase[0][0].Name + '_' + str(subname)
				model.add_member_dist_load(name, axis, initial * direction, final * direction)

			# Validate if the load is nodal
			elif 'Vertex' in load.ObjectBase[0][1][0]:
				numVertex = int(load.ObjectBase[0][1][0].split('Vertex')[1]) - 1
				vertex = load.ObjectBase[0][0].Shape.Vertexes[numVertex]
				
				node = list(filter(lambda element: element == [round(float(FreeCAD.Units.Quantity(vertex.Point.x,'mm').getValueAs(unitLength)), 2), round(float(FreeCAD.Units.Quantity(vertex.Point.z,'mm').getValueAs(unitLength)),2), round(float(FreeCAD.Units.Quantity(vertex.Point.y,'mm').getValueAs(unitLength)),2)], nodes_map))[0]
				indexNode = nodes_map.index(node)

				# subname = int(load.ObjectBase[0][1][0].split('Vertex')[1]) - 1
				name = str(indexNode)
				model.add_node_load(name, axis, float(load.NodalLoading.getValueAs(unitForce)) * direction)
			

					
		return model

	# Create the supports
	def setSuports(self, model, suports, nodes_map, unitLength):
		for suport in suports:
			suportvertex = list(suport.ObjectBase[0][0].Shape.Vertexes[int(suport.ObjectBase[0][1][0].split('Vertex')[1])-1].Point)
			for i, node in enumerate(nodes_map):
				if round(float(FreeCAD.Units.Quantity(suportvertex[0],'mm').getValueAs(unitLength)),2) == round(node[0],2) and round(float(FreeCAD.Units.Quantity(suportvertex[1],'mm').getValueAs(unitLength)),2) == round(node[2],2) and round(float(FreeCAD.Units.Quantity(suportvertex[2],'mm').getValueAs(unitLength)),2) == round(node[1],2):					
					name = str(i)
					model.def_support(name, suport.FixTranslationX, suport.FixTranslationZ, suport.FixTranslationY, suport.FixRotationX, suport.FixRotationZ, suport.FixRotationY)
					break
		
		return model

	def setMaterialAndSections(self, model, lines, unitLength, unitForce):
		materiais = []
		sections = []
		for line in lines:
			material = line.MaterialMember
			section = line.SectionMember

			if not material.Name in materiais:
				density = FreeCAD.Units.Quantity(material.Density).getValueAs('t/m^3') * 10 # Convert the input unit to t/m³ and then convert it to kN//m³
				density = float(FreeCAD.Units.Quantity(density, 'kN/m^3').getValueAs(unitForce+"/"+unitLength+"^3")) # Convert kN/m³ to the units defined in calc
				modulusElasticity = float(material.ModulusElasticity.getValueAs(unitForce+"/"+unitLength+"^2"))
				poissonRatio = float(material.PoissonRatio)
				G = modulusElasticity / (2 * (1 + poissonRatio))
				model.add_material(material.Name, modulusElasticity, G, poissonRatio, density)
				materiais.append(material.Name)
				

			if not section.Name in sections:

				ang = line.RotationSection.getValueAs('rad')
				J  = float(FreeCAD.Units.Quantity(section.MomentInertiaPolar, 'mm^4').getValueAs(unitLength+"^4"))
				A  = float(section.AreaSection.getValueAs(unitLength+"^2"))
				Iy = float(FreeCAD.Units.Quantity(section.MomentInertiaY, 'mm^4').getValueAs(unitLength+"^4"))
				Iz = float(FreeCAD.Units.Quantity(section.MomentInertiaZ, 'mm^4').getValueAs(unitLength+"^4"))
				Iyz = float(FreeCAD.Units.Quantity(section.ProductInertiaYZ, 'mm^4').getValueAs(unitLength+"^4"))

				
				# Aplica a rotação de eixo
				RIy = ((Iz + Iy) / 2 ) - ((Iz - Iy) / 2 )*math.cos(2 * ang) + Iyz * math.sin(2 * ang)
				RIz = ((Iz + Iy) / 2 ) + ((Iz - Iy) / 2 )*math.cos(2 * ang) - Iyz * math.sin(2 * ang)
				
				model.add_section(section.Name, A, RIy, RIz, J)
				sections.append(section.Name)
		
		return model

	
	def execute(self, obj):
		model = FEModel3D()
		# Filtra os diferentes tipos de elementos
		lines = list(filter(lambda element: 'Line' in element.Name or 'Wire' in element.Name, obj.ListElements))
		loads = list(filter(lambda element: 'Load' in element.Name, obj.ListElements))
		suports = list(filter(lambda element: 'Suport' in element.Name, obj.ListElements))

		nodes_map = self.mapNodes(lines, obj.LengthUnit)
		members_map = self.mapMembers(lines, nodes_map, obj.LengthUnit)

		model = self.setMaterialAndSections(model, lines, obj.LengthUnit, obj.ForceUnit)
		model = self.setNodes(model, nodes_map)
		model = self.setMembers(model, members_map, obj.selfWeight)
		model = self.setLoads(model, loads, nodes_map, obj.ForceUnit, obj.LengthUnit)
		model = self.setSuports(model, suports, nodes_map, obj.LengthUnit)

		model.analyze()

		# Generate the results
		momentz = []
		momenty = []
		mimMomenty = []
		mimMomentz = []
		maxMomenty = []
		maxMomentz = []
		axial = []
		torque = []
		minTorque = []
		maxTorque = []
		sheary = []
		shearz = []
		minSheary = []
		maxSheary = []
		minShearz = []
		maxShearz = []
		deflectiony = []
		minDeflectiony = []
		maxDeflectiony = []
		deflectionz = []
		minDeflectionz = []
		maxDeflectionz = []

		for name in model.members.keys():			
			momenty.append(','.join( str(value) for value in model.members[name].moment_array('My', obj.NumPointsMoment)[1]))
			momentz.append(','.join( str(value) for value in model.members[name].moment_array('Mz', obj.NumPointsMoment)[1]))

			sheary.append(','.join( str(value) for value in model.members[name].shear_array('Fy', obj.NumPointsShear)[1]))
			shearz.append(','.join( str(value) for value in model.members[name].shear_array('Fz', obj.NumPointsShear)[1]))

			axial.append(','.join( str(value) for value in model.members[name].axial_array(obj.NumPointsAxial)[1]))
			
			torque.append(','.join( str(value) for value in model.members[name].torque_array(obj.NumPointsTorque)[1]))

			deflectiony.append(','.join( str(value) for value in model.members[name].deflection_array('dy', obj.NumPointsDeflection)[1]))
			deflectionz.append(','.join( str(value) for value in model.members[name].deflection_array('dz', obj.NumPointsDeflection)[1]))

			mimMomenty.append(model.members[name].min_moment('My'))
			mimMomentz.append(model.members[name].min_moment('Mz'))
			maxMomenty.append(model.members[name].max_moment('My'))
			maxMomentz.append(model.members[name].max_moment('Mz'))

			minSheary.append(model.members[name].min_shear('Fy'))
			minShearz.append(model.members[name].min_shear('Fz'))
			maxSheary.append(model.members[name].max_shear('Fy'))
			maxShearz.append(model.members[name].max_shear('Fz'))

			minTorque.append(model.members[name].min_torque())
			maxTorque.append(model.members[name].max_torque())

			minDeflectiony.append(model.members[name].min_deflection('dy'))
			minDeflectionz.append(model.members[name].min_deflection('dz'))
			maxDeflectiony.append(model.members[name].max_deflection('dy'))
			maxDeflectionz.append(model.members[name].max_deflection('dz'))
			
			

		obj.NameMembers = model.members.keys()
		obj.Nodes = [FreeCAD.Vector(node[0], node[2], node[1]) for node in nodes_map]
		obj.MomentZ = momentz
		obj.MomentY = momenty
		obj.MinMomentY = mimMomenty
		obj.MinMomentZ = mimMomentz
		obj.MaxMomentY = maxMomenty
		obj.MaxMomentZ = maxMomentz
		obj.AxialForce = axial
		obj.Torque = torque
		obj.MinTorque = minTorque
		obj.MaxTorque = maxTorque
		obj.MinShearY = minSheary
		obj.MinShearZ = minShearz
		obj.MaxShearY = maxSheary
		obj.MaxShearZ = maxShearz
		obj.ShearY = sheary
		obj.ShearZ = shearz
		obj.DeflectionY = deflectiony
		obj.DeflectionZ = deflectionz
		obj.MinDeflectionY = minDeflectiony
		obj.MinDeflectionZ = minDeflectionz
		obj.MaxDeflectionY = maxDeflectiony
		obj.MaxDeflectionZ = maxDeflectionz
		
	   


	def onChanged(self,obj,Parameter):
		pass
	

class ViewProviderCalc:
	def __init__(self, obj):
		obj.Proxy = self
	

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


class CommandCalc():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/size.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+C", # a default shortcut (optional)
                "MenuText": "size structure",
                "ToolTip" : "Size the structure"}
    
    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("Part::FeaturePython", "Size")

        objSuport = Calc(obj, selection)
        ViewProviderCalc(obj.ViewObject)           

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("size", CommandSize())
