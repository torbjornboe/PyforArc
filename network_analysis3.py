import arcpy

import joins

import pathlib

import os

class Od_cost:

    def __init__(self,network, outgdb, **kwargs):

        def __kvargs_to_full_dict__(kwargs):
            vals =  {}
            for i in self.valid_matrixlayer_parameters:
                try:
                    vals[i] = kwargs[i]
                except KeyError:
                    vals[i] = None
            return vals
        
        self.network = network
        self.outgdb = outgdb
        #arcpy.env.overwriteOutput = True
        arcpy.env.workspace = self.outgdb
        self.valid_matrixlayer_parameters = ['layer_name', 'travel_mode', 'cutoff', 'number_of_destinations_to_find', 'time_of_day', 'time_zone', 'line_shape', 'accumulate_attributes']
        if kwargs:
            self.given_matrixlayer_parameters = __kvargs_to_full_dict__(kwargs)
            self.layer_name = self.given_matrixlayer_parameters['layer_name']
            self.travel_mode = self.given_matrixlayer_parameters['travel_mode']
            self.cutoff = self.given_matrixlayer_parameters['cutoff']
            self.number_of_destinations_to_find = self.given_matrixlayer_parameters['number_of_destinations_to_find']
            self.time_of_day = self.given_matrixlayer_parameters['time_of_day']
            self.time_zone = self.given_matrixlayer_parameters['time_zone']
            self.line_shape = self.given_matrixlayer_parameters['line_shape']
            self.accumulate_attributes = self.given_matrixlayer_parameters['accumulate_attributes']
        self.matrixlayer = arcpy.na.MakeODCostMatrixAnalysisLayer(network, self.layer_name, self.travel_mode, self.cutoff, self.number_of_destinations_to_find, self.time_of_day, self.time_zone, self.line_shape, self.accumulate_attributes)
        self.odcost_layer = self.matrixlayer.getOutput(0)
        self.sublayer_names = arcpy.na.GetNAClassNames(self.odcost_layer)
        self.origins_layer_name = self.sublayer_names["Origins"]
        self.destinations_layer_name = self.sublayer_names["Destinations"]
        
        


    def add_origins(self,origins,identifier,search_tolerance):
        self.origins_identifierfield = identifier
        self.origins = origins
        self.origins_search_tolerance = search_tolerance
        field_mappings = arcpy.na.NAClassFieldMappings(self.odcost_layer, self.origins_layer_name)
        field_mappings["Name"].mappedFieldName = self.origins_identifierfield
        arcpy.na.AddLocations(self.odcost_layer, self.origins_layer_name, self.origins, field_mappings,
                          self.origins_search_tolerance)

    def add_destinations(self,destinations,identifier,searchtolerance):
        self.destinations = destinations
        self.destinations_identifierfield = identifier
        self.destinations_search_tolerance = searchtolerance
        field_mappings = arcpy.na.NAClassFieldMappings(self.odcost_layer, self.destinations_layer_name)
        field_mappings["Name"].mappedFieldName = self.destinations_identifierfield
        arcpy.na.AddLocations(self.odcost_layer, self.destinations_layer_name, self.destinations, field_mappings, self.destinations_search_tolerance)

    def solve(self):
        arcpy.na.Solve(self.odcost_layer)
        # except arcgisscripting.ExecuteError ?

    def __get_na_layer_path__(self,descr, alias):
        for item in descr['children']:
            try:
                if item['aliasName'] == alias:
                    return item['dataElement']['catalogPath']
            except KeyError:
                print('make a base validataion class')

    

    def origins_to_lines(self):
        descr = arcpy.da.Describe(self.odcost_layer)
        self.lines_path = self.__get_na_layer_path__(descr,'Lines')
        
        self.origings_path = self.__get_na_layer_path__(descr,'Origins')
        self.origings_path_path = pathlib.Path(self.origings_path)
        self.origings_path_name = self.origings_path_path.name
        
        arcpy.AddXY_management(self.origings_path)
        #print(origings_path, destinations_path, lines_path)
        joins.join_1one1(self.origings_path, 'ObjectID', self.outgdb, self.lines_path, 'OriginID', ['Name','POINT_X','POINT_Y'])
        
        joins.join_1one1(self.origins,'OBJECTID',self.outgdb,self.lines_path,f'Name_{self.origings_path_name}', from_fields = 'all')
        

    def destinations_to_lines(self):

        descr = arcpy.da.Describe(self.odcost_layer)
        self.lines_path = self.__get_na_layer_path__(descr,'Lines')
        
        self.destinations_path = self.__get_na_layer_path__(descr,'Destinations')
        self.destinations_path_path = pathlib.Path(self.destinations_path)
        self.destinations_path_name = self.destinations_path_path.name
        
        arcpy.AddXY_management(self.destinations_path)
        joins.join_1one1(self.destinations_path, 'ObjectID', self.outgdb, self.lines_path, 'DestinationID', ['Name','POINT_X','POINT_Y'])
        joins.join_1one1(self.destinations,'OBJECTID',self.outgdb,self.lines_path,f'Name_{self.destinations_path_name}', from_fields = 'all')
        #arcpy.AddXY_management(self.destinations_path)

    def multiple_origins(self, outname, outgdb = self.outgdb):
        #make one point on origin for every line
        arcpy.CreateFeatureclass_management(outgdb, outname, 'POINT', template = self.lines_path, spatial_reference = self.lines_path)
        fieldx = [field.name for field in arcpy.ListFields(fc,'POINT_X_Origins*')]
        fieldy = [field.name for field in arcpy.ListFields(fc,'POINT_Y_Origins*')]
        fields = [field.name for field in arcpy.ListFields(outname) if field.name not in ['Shape','ObjectID']+fieldx+fieldy]
        
        
        insertcursor = arcpy.da.InsertCursor(outname, fields + ['@shape'])
        searchcursor = arcpy.da.SearchCursor(self.lines, fields + fieldsxy)
        inndata = []

        for i,row in enumerate(searchcursor): #append fields exept POINT_X and POINT_Y
            data = []
            point = arcpy.Point(row[-2], row[-1])
            geom = arcpy.PointGeometry(point)#dont think I need spatial ref
            inndata.append(list(row[:-2]))
            inndata[i].append(geom)

        for item in inndata:
            for row in insertcursor:
                row.insertRow(item)
                

    def summarize_on_origins(self):
        #make one point on orgin where line data is summarized
        pass

        
##
##
##    odcost_layer = od_cost.getOutput(0)
##
##    sublayer_names = arcpy.na.GetNAClassNames(odcost_layer)
##    origins_layer_name = sublayer_names["Origins"]
##    destinations_layer_name = sublayer_names["Destinations"]
##
##    # arcpy.da.Describe(odcost_layer)
##    #'dataElement': {
##    #		'catalogPath': 'C:\\Users\\torbjorn.boe\\Google Drive\\Python\\PyforArc\\tests\\testdata.gdb\\ODCostMatrix2\\Origins2',
##    #		'FIDSet': None,
##    #		'aliasName': 'Origins',
##    #		'areaFieldName': '',
##    #		'baseName': 'Origins2',
##
##    # test slutt
##
##    
##
##    ##
##
##    # layer_object.saveACopy(output_layer_file)


##if __name__ == '__main__':
##    nd = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\test_odcost.gdb\test_na\test_na_ND'
##    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
##    origins = 'plants'
##    destinations = 'trees'
##    odcost = Od_cost(nd,gdb,line_shape = 'STRAIGHT_LINES', travel_mode = 'walktime', cutoff = 10, layer_name = 'testname', number_of_destinations_to_find = 1)
##    odcost.add_origins(origins,'OBJECTID',500)
##    odcost.add_destinations(destinations,'OBJECTID',500)
##    odcost.solve()
##    odcost.origins_to_lines()
##    odcost.destinations_to_lines()
