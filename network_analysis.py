import arcpy

import joins

import pathlib

import os

class Od_cost:
    """
    this class makes a OD-cost matrikx layer and featureclasses from the solve
    is stored in outgdb.
    network -- string, path to network layer
    outgdb -- string, path to outgdb
    optional argurments:
    travel_mode -- string, name of travelmode defined in network layer
    cutoff -- float or integer, max cost (distance, minutes) for calculation
    number_of_destinations -- integer, number of destinations to find. Defaults to all
    time_of_day -- string, date and time
    line_shape -- string, NO_LINES or STRAIGHT_LINES 
    time_zone -- string, LOCAL_TIME_AT_LOCATIONS or UTC
    accumulate_attributes -- list, List of cost attributes to be accumulated during analysis.  
    """
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
        """
        origins -- string, path to origin featureclass
        identifier -- string, field holding uniqe identifying values
        search_tolerance -- integer, searchtolerance for conecting origin to network
        """
        self.origins_identifierfield = identifier
        self.origins = origins
        self.origins_search_tolerance = search_tolerance
        field_mappings = arcpy.na.NAClassFieldMappings(self.odcost_layer, self.origins_layer_name)
        field_mappings["Name"].mappedFieldName = self.origins_identifierfield
        arcpy.na.AddLocations(self.odcost_layer, self.origins_layer_name, self.origins, field_mappings,
                          self.origins_search_tolerance)

    def add_destinations(self,destinations,identifier,searchtolerance):
        """
        origins -- string, path to origin featureclass
        identifier -- string, field holding uniqe identifying values
        search_tolerance -- integer, searchtolerance for conecting origin to network
        """
        self.destinations = destinations
        self.destinations_identifierfield = identifier
        self.destinations_search_tolerance = searchtolerance
        field_mappings = arcpy.na.NAClassFieldMappings(self.odcost_layer, self.destinations_layer_name)
        field_mappings["Name"].mappedFieldName = self.destinations_identifierfield
        arcpy.na.AddLocations(self.odcost_layer, self.destinations_layer_name, self.destinations, field_mappings, self.destinations_search_tolerance)

    def solve(self):
        """
        solves odcost_layer
        """
        arcpy.na.Solve(self.odcost_layer)
        # except arcgisscripting.ExecuteError ?

    def __get_na_layer_path__(self,descr, alias):
        """
        internal method for getting layerpath from arcpy.da.Describe dictionary
        descr -- dictionary, arcpy.da.Describe dictionary on odcost_layer
        alias -- string, aliasname of alias the object path is wanted for
        """
        for item in descr['children']:
            try:
                if item['aliasName'] == alias:
                    return item['dataElement']['catalogPath']
            except KeyError:
                print('make a base validataion class')

    

    def origins_to_lines(self):
        """
        joins origins to lines and adds POINT_X, POINT_Y fields
        """
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
        """
        joins destinations  to lines and adds POINT_X, POINT_Y fields
        """

        descr = arcpy.da.Describe(self.odcost_layer)
        self.lines_path = self.__get_na_layer_path__(descr,'Lines')
        
        self.destinations_path = self.__get_na_layer_path__(descr,'Destinations')
        self.destinations_path_path = pathlib.Path(self.destinations_path)
        self.destinations_path_name = self.destinations_path_path.name
        
        arcpy.AddXY_management(self.destinations_path)
        joins.join_1one1(self.destinations_path, 'ObjectID', self.outgdb, self.lines_path, 'DestinationID', ['Name','POINT_X','POINT_Y'])
        joins.join_1one1(self.destinations,'OBJECTID',self.outgdb,self.lines_path,f'Name_{self.destinations_path_name}', from_fields = 'all')
        #arcpy.AddXY_management(self.destinations_path)

    def multiple_origins(self, outname, outgdb, overwrite = True):
        """"
        Makes a featureclass with one "origin" for every line. Use Dissolve for generating statistics and reduce to one feature.
        outgdb -- string, path to gdb for placeing result
        outname -- string, name of result featureclass
        overwrite -- BOOL, True or False. Defaults to True. Result can be overwriten.
        """
        #make one point on origin for every line
        arcpy.env.overwriteOutput = overwrite
        arcpy.CreateFeatureclass_management(outgdb, outname, 'POINT', template = self.lines_path, spatial_reference = self.lines_path)
        fieldx = [field.name for field in arcpy.ListFields(outname,'POINT_X_Origins*')]
        fieldy = [field.name for field in arcpy.ListFields(outname,'POINT_Y_Origins*')]
        fields = [field.name for field in arcpy.ListFields(outname) if field.name not in ['Shape','ObjectID']+fieldx+fieldy]
        
        
        insertcursor = arcpy.da.InsertCursor(outname, fields + ['SHAPE@'])
        searchcursor = arcpy.da.SearchCursor(self.lines_path, fields + fieldx + fieldy)
        inndata = []

        for i,row in enumerate(searchcursor): #append fields exept POINT_X and POINT_Y
            data = []
            point = arcpy.Point(row[-2], row[-1])
            geom = arcpy.PointGeometry(point)#dont think I need spatial ref
            inndata.append(list(row[:-2]))
            inndata[i].append(geom)

        for item in inndata:
            print(item)
            insertcursor.insertRow(item)



