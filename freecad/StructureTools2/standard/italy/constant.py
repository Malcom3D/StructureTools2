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
    def __init__(self):
        pass

    def Q1map(self):
        # Overloads by intended use [ntc2018 Tab. 3.1.II]
        # - uniformly distributed vertical loads qk
        # - concentrated vertical loads Qk
        # - linear horizontal loads Hk

        # mapped list ['description', qk, Qk, Hk, psi0j, psij1, psi2j]
        self.Q1mapList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        self.Q1mapList.append(list(map(set_type, ['Cat.A  Areas for domestic and residential activities', '2.00', '2.00', '1.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.A  Common stairs, balconies, landings', '4.00', '4.00', '2.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B1 Offices not open to the public', '2.00', '2.00', '1.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B2 Offices open to the public', '3.00', '2.00', '1.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.B  Common stairs, balconies and landings', '4.00', '4.00', '2.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C1 Areas with tables', '3.00', '3.00', '1.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C2 Areas with fixed seating', '4.00', '4.00', '2.00', '0.70', '0.70', '0.60', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C3 Environments without obstacles to the movement of people', '5.00', '5.00', '3.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C4 Areas where physical activities may be carried out', '5.00', '5.00', '3.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C5 Areas susceptible to large crowds', '5.00', '5.00', '3.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat.C Common stairways, balconies and landings', '4.00', '4.00', '2.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. D1 Shops', '4.00', '4.00', '2.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. D2 Shopping centers, markets, department stores', '5.00', '5.00', '2.00', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. D Common stairs, balconies and landings', '0.0', '0.0', '0.0', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. E1 Areas for accumulation of goods and related access areas', '6.00', '7.00', '1.00', '1.00', '0.90', '0.80'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. E2 Environments for industrial use', '0.0', '0.0', '0.0', '1.00', '0.90', '0.80'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. F Garages, traffic, parking and stopping areas of light vehicles (< 30 KN)', '2.50', '20.0', '1.0', '0.70', '0.70', '0.60'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. G Areas for traffic and parking of medium vehicles ( 30 kN <> 160 kN)', '5.00', '100.00', '1.00', '0.70', '0.50', '0.30'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. H Accessible roofs for maintenance and repair only', '0.50', '1.20', '1.0', '0.0', '0.0', '0.0'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. I Accessible roofs for environments of category of use between A and D', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0'])))
        self.Q1mapList.append(list(map(set_type, ['Cat. K Roofs for special uses, such as equipment, heliports', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0'])))

        return self.Q1mapList

    def psi(self, index, Elevation):
        # Combination coefficients [ntc2018 Tab. 2.5.I]
        # Overloads by natural action type [ntc2018 Tab. 3.1.II]
        # Wind [ntc2018 3.3]
        # Snow [ntc2018 3.4]
        # Temperature [ntc2018 3.5]
        # mapped list ['description', psi0j, psij1, psi2j]
        psiList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        psiList.append(list(map(set_type, ['Q1', self.Q1mapList[index][4], self.Q1mapList[index][5], self.Q1mapList[index][6]])))
        psiList.append(list(map(set_type, ['Wind', '0.6', '0.2', '0.0'])))
        psiList.append(list(map(set_type, ['Temperature', '0.6', '0.5', '0.0'])))
        if Elevation < 1000:
            psiList.append(list(map(set_type, ['Snow', '0.5', '0.2', '0.0'])))
        else:
            psiList.append(list(map(set_type, ['Snow', '0.7', '0.5', '0.2'])))

        return psiList

    def Strength(self):
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

    def Gamma(self):
        # Gamma[G1, G2, Qi]: Partial coefficients for actions/loads or for the effect of actions/loads in SLU checks [ntc2018 Tab. 2.6.I]
        # mapped list ['LoadType', 'GammaFavourable EQU', 'GammaFavourable A1', 'GammaFavourable A2', 'GammaUnfavourable EQU', 'GammaUnfavourable A1', 'GammaUnfavourable A2',]
        GammaList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        GammaList.append(list(map(set_type, ['G1', '0.9', '1.0', '1.0', '1.1', '1.3', '1.0'])))
        GammaList.append(list(map(set_type, ['G2', '0.8', '0.8', '0.8', '1.5', '1.5', '1.3'])))
        GammaList.append(list(map(set_type, ['Qi', '0.0', '0.0', '0.0', '1.5', '1.5', '1.3'])))

        return GammaList

    def GammaM(self):
        # Gamma[mA, mB]: Coefficienti parziali per tipo di materiale [ntc2018 Tab. 4.4.III]
        # mapped list ['WoodType', 'GammaMa', 'GammaMb']
        self.GammaMList = [list(map(set_type, ['', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        self.GammaMList.append(list(map(set_type, ['Solid wood', '1.50', '1.45'])))
        self.GammaMList.append(list(map(set_type, ['Glued laminated timber', '1.45', '1.35'])))
        self.GammaMList.append(list(map(set_type, ['Cross-laminated board panels', '1.45', '1.35'])))
        self.GammaMList.append(list(map(set_type, ['Particle or fibreboard panels', '1.50', '1.40'])))
        self.GammaMList.append(list(map(set_type, ['LVL, plywood, oriented strand boards', '1.40', '1.30'])))
        self.GammaMList.append(list(map(set_type, ['Unions', '1.50', '1.40'])))
        self.GammaMList.append(list(map(set_type, ['Exceptional combinations', '1.00', '1.00'])))

        return self.GammaMList

    def Kdef(self):
        # Kdef: Classe di servizio [ntc2018 Tab. 4.4.V]
        # mapped list ['WoodType', 'UNIENRef', 'ServiceClass1', 'ServiceClass2', 'ServiceClass3']
        self.KdefList = [list(map(set_type, ['', '', '0.0', '0.0', '0.0']))]
        self.KdefList.append(list(map(set_type, ['Solid wood', 'UNI EN 14081-1', '0.60', '0.80', '2.00'])))
        self.KdefList.append(list(map(set_type, ['Glued laminated timber', 'UNI EN 14080', '0.60', '0.80', '2.00'])))
        self.KdefList.append(list(map(set_type, ['LVL', 'UNI EN 14374', 'UNI EN 14279', '0.60', '0.80', '2.00'])))
        self.KdefList.append(list(map(set_type, ['Plywood', 'UNI EN 636:2015', '0.80', '1.00', '2.50'])))
        self.KdefList.append(list(map(set_type, ['Oriented Strand Board (OSB)', 'UNI EN 300:2006 OSB/2', '2.25', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Oriented Strand Board (OSB)', 'UNI EN 300:2006 OSB/3 OSB/4', '1.50', '2.25', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 312:2010 Part 4', '2.25', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 312:2010 Part 5', '2.25', '3.00', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 312:2010 Part 6', '1.50', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 312:2010 Part 7', '1.50', '2.25', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Fibreboard hardboard', 'UNI EN 622-2::2005 HB.LA 2.25', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Fibreboard hardboard', 'UNI EN 622-2::2005 HB.HLA1,HB.HLA2 2.25', '3.00', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Fibreboard semi-hardboard', 'UNI EN 622-3:2005 MBH.LA1, MBH.LA2', '3.00', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Fibreboard semi-hardboard', 'UNI EN 622-3:2005 MBH.HLS1, MBH.HLS2', '3.00', '4.00', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Dry-processed wood fibreboard (MDF)', 'UNI EN 622-5:2010 MDF.LA', '2.25', '0.0', '0.0'])))
        self.KdefList.append(list(map(set_type, ['Dry-processed wood fibreboard (MDF)', 'UNI EN 622-5:2010 MDF.HLS', '2.25', '3.00', '0.0'])))

        return self.KdefList

    def Kmod(self):
        # Kmod: Classe di servizio, Classe di durata del carico [ntc2018 Tab. 4.4.IV]
        # mapped list ['WoodType', 'UNIENRef', 'ServiceClass', 'Permanent', 'Long', 'Medium', 'Short', 'Instant', 'Kdef', 'GammaMa', 'GammaMb']
        self.KmodList = [list(map(set_type, ['', '', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']))]
        self.KmodList.append(list(map(set_type, ['Solid wood', 'UNI EN 14081-1', '1', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[1][2], self.GammaMList[1][1], self.GammaMList[1][2]])))
        self.KmodList.append(list(map(set_type, ['Solid wood', 'UNI EN 14081-1', '2', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[1][3], self.GammaMList[2][1], self.GammaMList[2][2]])))
        self.KmodList.append(list(map(set_type, ['Solid wood', 'UNI EN 14081-1', '3', '0.50', '0.55', '0.65', '0.70', '0.90', self.KdefList[1][4], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Glued laminated timber', 'UNI EN 14080', '1', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[2][2], self.GammaMList[1][1], self.GammaMList[1][2]])))
        self.KmodList.append(list(map(set_type, ['Glued laminated timber', 'UNI EN 14080', '2', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[2][3], self.GammaMList[2][1], self.GammaMList[2][2]])))
        self.KmodList.append(list(map(set_type, ['Glued laminated timber', 'UNI EN 14080', '3', '0.50', '0.55', '0.65', '0.70', '0.90', self.KdefList[2][4], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['LVL', 'UNI EN 14374, UNI EN 14279', '1', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[3][2], self.GammaMList[1][1], self.GammaMList[1][2]])))
        self.KmodList.append(list(map(set_type, ['LVL', 'UNI EN 14374, UNI EN 14279', '2', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[3][3], self.GammaMList[2][1], self.GammaMList[2][2]])))
        self.KmodList.append(list(map(set_type, ['LVL', 'UNI EN 14374, UNI EN 14279', '3', '0.50', '0.55', '0.65', '0.70', '0.90', self.KdefList[3][4], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Plywood', 'UNI EN 636:2015', '1', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[4][2], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Plywood', 'UNI EN 636:2015', '2', '0.60', '0.70', '0.80', '0.90', '1.10', self.KdefList[4][3], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Plywood', 'UNI EN 636:2015', '3', '0.50', '0.55', '0.65', '0.70', '0.90', self.KdefList[4][4], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Oriented strand board (OBS)', 'UNI EN 300:2006, OSB/2', '1', '0.30', '0.45', '0.65', '0.85', '1.10', self.KdefList[5][2], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Oriented strand board (OBS)', 'UNI EN 300:2006, OSB/3, OSB/4', '1', '0.40', '0.50', '0.70', '0.90', '1.10', self.KdefList[6][2], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Oriented strand board (OBS)', 'UNI EN 300:2006, OBS/3, OSB/4', '2', '0.30', '0.40', '0.55', '0.70', '0.90', self.KdefList[6][3], self.GammaMList[5][1], self.GammaMList[5][2]])))
        self.KmodList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 300:2006, Part 4, 5', '1', '0.40', '0.45', '0.65', '0.85', '1.10', self.KdefList[7][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 300:2006, Part 5', '2', '0.20', '0.30', '0.45', '0.60', '0.80', self.KdefList[8][3], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 300:2006, Part 6, 7', '1', '0.40', '0.50', '0.70', '0.90', '1.10', self.KdefList[9][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Particle board (chipboard)', 'UNI EN 300:2006, Part 7', '2', '0.30', '0.40', '0.55', '0.70', '0.90', self.KdefList[10][3], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, hardboard', 'UNI EN 622-2:2005, HB.LA, HB.HLA 1 or 2', '1', '0.30', '0.45', '0.65', '0.85', '1.10', self.KdefList[11][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, hardboard', 'UNI EN 622-2:2005, HB.HLA 1 or 2', '2', '0.20', '0.30', '0.45', '0.60', '0.80', self.KdefList[12][3], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, semi-hardboard', 'UNI EN 622-3:2005, MBH.LA1 or 2', '1', '0.20', '0.40', '0.60', '0.80', '1.10', self.KdefList[13][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, semi-hardboard', 'UNI EN 622-3:2005, MBH.HLS1 or 2', '1', '0.20', '0.40', '0.60', '0.80', '1.10', self.KdefList[14][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, semi-hardboard', 'UNI EN 622-3:2005, MBH.HLS1 or 2', '2', '0.0', '0.0', '0.0', '0.45', '0.80', self.KdefList[14][3], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, dry-processed (MDF)', 'UNI EN 622-5:2010, MDF.LA, MDF.HLS', '1', '0.20', '0.40', '0.60', '0.80', '1.10', self.KdefList[15][2], self.GammaMList[4][1], self.GammaMList[4][2]])))
        self.KmodList.append(list(map(set_type, ['Fiberboard, dry-processed (MDF)', 'UNI EN 622-5:2010, MDF.HLS', '2', '0.0', '0.0', '0.0', '0.45', '0.80', self.KdefList[16][3], self.GammaMList[4][1], self.GammaMList[4][2]])))

        return self.KmodList
