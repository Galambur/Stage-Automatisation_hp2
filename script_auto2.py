import os
import sys
import inspect
import processing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
      
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]      

class automa(QWidget):
    def __init__(self, parent=None):
        self.iface = iface
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()

        # Add the radio buttons
        self.open_file = QPushButton("Ouvrir un fichier .csv")

        # Connect radio buttons to our functions
        self.open_file.clicked.connect(self.func_open)

        #Add the widgets to the layout:
        self.layout.addWidget(self.open_file)

        #Set the layout:
        self.setLayout(self.layout)  
        self.setWindowTitle("Fichier CSV")

    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'logo.jpg'))
      self.action = QAction(QIcon(icon), 'Trame automatique hp2', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Trame auto hp2', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('Trame auto hp2', self.action)  
      del self.action

    def run(self):
        self.iface.messageBar().pushMessage("L'extension 'script auto hp2' a été lancée")
        button.show() #shows our widgets
        button.activateWindow() ## met le widget au premier plan
      
      
    def func_open(self, on):
        self.close()
        filename1 = QFileDialog.getOpenFileName(caption='Choisissez un fichier csv', filter=("CSV files(*.csv);;All files(*.*)"))
        if ((filename1[0].find(".csv")) == -1):
            iface.messageBar().pushWarning('Attention ', 'Veuillez choisir un fichier en .csv')
        else:
            filename = filename1[0]
            mainPlugin(filename)
            
class interface(QWidget):
    def __init__(self, parent=automa):
        self.iface = iface
        super(interface, self).__init__()
        self.layout2 = QHBoxLayout()

            # Add the push buttons
        self.open_layer = QPushButton("Une couche")
        self.open_file = QPushButton("Un fichier")

            # Connect push buttons to our functions
        self.open_layer.clicked.connect(self.select_layer)
        self.open_file.clicked.connect(self.func_open)

            #Add the widgets to the layout:
        self.layout2.addWidget(self.open_layer)
        self.layout2.addWidget(self.open_file)

            #Set the layout:
        self.setLayout(self.layout2)  
        self.setWindowTitle("Deuxième couche pour l'intersection")
        
    def run():
        inter.show()
        inter.activateWindow() ## met le widget au premier plan
                
    def func_open(self, on):
        self.close()
        filename1 = QFileDialog.getOpenFileName(caption='Choisissez un fichier csv')
        if (filename1[0] == ''):  ## no file selected
            self.show()
            iface.messageBar().pushWarning('Attention ', 'Veuillez choisir un fichier')
        else:
            filename = filename1[0]
            self.close()
            part2(str(filename))
        
    def select_layer(self, on):
        self.close()
        layer = iface.activeLayer()
        items = ([layer.name() for layer in QgsProject.instance().mapLayers().values()])
        item, ok = QInputDialog.getItem(self, "Choisissez une couche", 
                 "Liste des couches", items, 0, False) # get field to delete with selector
        if ok and item:
            layer_name=item
            
            layer_chosen = QgsProject.instance().mapLayersByName( layer_name )[0]
            
            myfilepath = layer_chosen.dataProvider().dataSourceUri()

            (myDirectory,nameFile) = os.path.split(myfilepath)
                
            item_file = myDirectory + r"/"  # on ne peut pas concatener un backslash en python
            item_file = item_file + layer_name + '.shp' 
            self.close()
            part2(str(item_file))
        elif not ok:
            self.show()
        else : 
            iface.messageBar().pushWarning("Erreur", "Vous n'avez pas entré de couche à utiliser")

button = automa()

inter=interface()


########## MAIN FUNCTION ########## 

def mainPlugin(filename_received):
    iface.messageBar().pushMessage('La trame commence')
    convert_csv(filename_received) 
    add_fields()    
    fields_to_delete = ['Nature_urg', 'ind_col', 'gcod_date', 'gcod_niv', 'gcod_valid', 'id_unique']
    delete_fields(fields_to_delete)   
    concat()
    interface.run()
    
def part2(file_to_join):
    jointure(file_to_join)
    copy_fields('CODE_IRIS', 'champ3', file_to_join)
    change_names('X_Lambert_', 'X_L93')
    change_names('Y_Lambert_', 'Y_L93')
    fields_to_delete = ['ROWID', 'Batiment', 'Escalier', 'Adresse_su', 'nature_urg', 'Ind_col','cle_HP4', 'CODE_IRIS', 'INSEE_COM','NOM_COM', 'IRIS', "NOM_IRIS", 'TYP_IRIS', 'ANNEE']
    delete_fields(fields_to_delete)       

        ########## CONVERTING .csv TO .shp ##########
def convert_csv(filename_received):    
    # recuperation du chemin du fichier choisi juste avant et creation du nom complet du fichier à créer
    path_name = filename_received.rsplit('/', 1) 
    path_name[0] = path_name[0] + "/"
    filename_shp = getTextInput("Nouveau nom .shp", "Entrez un nom pour votre fichier shp :")
    
    Input_Table = filename_received # the filepath for the input CSV
    lon_field = 'Longitude' # the name for the field containing the longitude
    lat_field = 'Latitude' # the name for the field containing the latitude
    crs = 4326 # the crs as needed
    Output_Layer = path_name[0] + filename_shp  # the filepath for the output shapefile
         
    spatRef = QgsCoordinateReferenceSystem(crs, QgsCoordinateReferenceSystem.EpsgCrsId)
         
    inp_tab = QgsVectorLayer(Input_Table, 'Input_Table', 'ogr')
    prov = inp_tab.dataProvider()
    fields = inp_tab.fields()
    outLayer = QgsVectorFileWriter(Output_Layer, None, fields, 0, spatRef, driverName='ESRI Shapefile')

    pt = QgsPointXY()
    outFeature = QgsFeature()

    for feat in inp_tab.getFeatures():
        attrs = feat.attributes()
        pt.setX(float(feat[lon_field].replace(',','.')))
        pt.setY(float(feat[lat_field].replace(',','.')))
        outFeature.setAttributes(attrs)
        outFeature.setGeometry(QgsGeometry.fromPointXY(pt))
        outLayer.addFeature(outFeature)
    del outLayer

        # ouverture de la nouvelle couche crée
    vlayer = QgsVectorLayer(Output_Layer + '.shp', filename_shp, "ogr")
    if not vlayer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(vlayer)


        ########## AJOUT DES COLONNES ##########
def add_fields():  
    layer = iface.activeLayer()  
    name_fields = ['indic_vent', 'champ1', 'champ2', 'champ3', 'ID_parcell']
    
    for i in range(len(name_fields)):
        field_to_add = layer.fields().indexFromName(name_fields[i])
        field_name = name_fields[i]
        if field_to_add == -1 : 
            layer.dataProvider().addAttributes([ QgsField(field_name, QVariant.String, len=250) ])
        else :
            print("La colonne '", field_name, "' existe déjà")
            

    field_to_add = layer.fields().indexFromName('sim_nb_lgt')
    if field_to_add == -1 :
        layer.dataProvider().addAttributes([ QgsField('sim_nb_lgt', QVariant.Double) ])
    else : 
        print("La colonne numero ", field_to_add, " (sim_nb_lgt) existe déjà")
    layer.updateFields()
    
    
    field_to_add = layer.fields().indexFromName('sim_an_vte')
    if field_to_add == -1 :
        layer.dataProvider().addAttributes([ QgsField('sim_an_vte', QVariant.Date) ])
    else : 
        print("La colonne numero ", field_to_add, " (sim_an_vte) existe déjà")
    layer.updateFields()
    

    field_to_add = layer.fields().indexFromName('sim_vte')
    if field_to_add == -1 :
        layer.dataProvider().addAttributes([ QgsField('sim_vte', QVariant.String, len=50) ])
    else : 
        print("La colonne numero ", field_to_add, " (sim_vte) existe déjà")
    layer.updateFields()



        ######### COPIE DES VALEURS DE id_unique DANS champ2 ##########☻
def copy_fields(field_to_copy, field_to_paste, file_to_join):
    
    layer = iface.activeLayer()
    
    id_field_to_copy = layer.fields().indexFromName(field_to_copy)
    if id_field_to_copy != -1 :
        with edit(layer):
            for feature in layer.getFeatures():
                feature.setAttribute(feature.fieldNameIndex(field_to_paste), feature[field_to_copy])
                layer.updateFeature(feature)
    else :
        print("La colonne '", field_to_copy,"' n'existe pas")
            


        ########## SUPPRIMER COLONNES ###########
def delete_fields(fields_to_delete):
    layer = iface.activeLayer()    
    
    for i in range(len(fields_to_delete)):
        field_to_delete = layer.fields().indexFromName(fields_to_delete[i])

        if field_to_delete != -1 :
            with edit(layer):
                layer.dataProvider().deleteAttributes([field_to_delete]) 
        layer.updateFields()



        ########## CHANGEMENT DE NOMS ##########
def change_names(old_name, new_name):
    layer = iface.activeLayer()
    field_index = layer.fields().indexFromName(old_name)
    if field_index != -1:
        with edit(layer):
            layer.renameAttribute(field_index, new_name)
            layer.updateFields


        ######### CONCAT champ2 ##########
def concat():
    layer = iface.activeLayer()
    for feature in layer.getFeatures():
        lat = str(feature['Latitude']).replace(',', '.')
        lon = str(feature['Longitude']).replace(',', '.')
        value = 'http://maps.google.com/maps?q=&hl=fr&ie=UTF8&ll=' + lat + ',' + lon + '&layer=c&cbll=' + lat + ',' + lon + '&cbp=12,238.42,,0,0'
        with edit(layer):
            feature.setAttribute(feature.fieldNameIndex('champ2'), value)
            layer.updateFeature(feature)


        ######### JOINTURE SPATIALE ##########
def jointure(file_to_join):
    fnin = iface.activeLayer()
    
    myfilepath = iface.activeLayer().dataProvider().dataSourceUri()

    (myDirectory,nameFile) = os.path.split(myfilepath)

    file_input = myDirectory + '/' +  fnin.name() + '.shp'
    if ((file_input.find(".shp")) != -1):
        iface.messageBar().pushMessage("Selectionnez un deuxième fichier pour la jointure spatiale")
        file_input2 = file_to_join
        if ((file_input2.find(".shp")) != -1):
            file_out = QFileDialog.getSaveFileName(caption='Enregistrer sous', filter=("SHP files(*.shp);;All files(*.*)"))
            fnout = file_out[0]
        
            processing.run("qgis:joinattributesbylocation", {'INPUT':file_input, 'JOIN':file_input2, 'PREDICATE':[0], 'JOIN_FIELDS':[], 'METHOD':0, 'DISCARD_NONMATCHING':False, 'PREFIX':'', 'OUTPUT':fnout}) 

            iface.addVectorLayer(fnout,'','ogr')



        ######### TEXT INPUT ##########
def getTextInput(title, message):
    answer = QInputDialog.getText(None, title, message)
    if answer[1]:
        return answer[0]
    else:
        return None
