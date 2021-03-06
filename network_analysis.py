import arcpy

import joins

import pathlib, json, os
from collections import Counter


class Od_cost:
    """
    this class makes a OD-cost matrix layer. Featureclasses from the solve
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

    Methods:
    add_origins -- adds origins. Must be run before solve
    add_destinations -- adds destinations. Must be run before solve
    solve -- run solve
    origins_to_lines -- adds xy fields to origins and joins origins to lines
    destinations_to_lines -- adds xy fields to destinations and joins destinations to lines
    multiple_origins -- makes a point for every unike origin-line pair. This can be further prosessed
    with e.g. dissolve to make aggregations.
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
        self.matrixlayer = arcpy.na.MakeODCostMatrixAnalysisLayer(network, self.layer_name, self.travel_mode,
                                                                  self.cutoff, self.number_of_destinations_to_find,
                                                                  self.time_of_day, self.time_zone, self.line_shape,
                                                                  self.accumulate_attributes)
        self.odcost_layer = self.matrixlayer.getOutput(0)
        self.sublayer_names = arcpy.na.GetNAClassNames(self.odcost_layer)
        self.origins_layer_name = self.sublayer_names["Origins"]
        self.destinations_layer_name = self.sublayer_names["Destinations"]
        self.__solve = False
        


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
        self.__solve = True
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
        print('method origins to lines'.upper())
        if not self.__solve:
            print('run solve first')
            raise TypeError
        descr = arcpy.da.Describe(self.odcost_layer)
        self.lines_path = self.__get_na_layer_path__(descr,'Lines')
        
        self.origings_path = self.__get_na_layer_path__(descr,'Origins')
        self.origings_path_path = pathlib.Path(self.origings_path)
        self.origings_path_name = self.origings_path_path.name
        
        arcpy.AddXY_management(self.origings_path)
        #adding x and y fields to lines
        print('joining x  and y to line'.upper())
        joins.join_1one1(self.origings_path, 'ObjectID', self.outgdb, self.lines_path, 'OriginID', ['Name','POINT_X','POINT_Y'])
        print(f'joining {self.origins} to {self.lines_path}'.upper())
        joins.join_1one1(self.origins, self.origins_identifierfield, self.outgdb, self.lines_path, f'Name_{self.origings_path_name}', from_fields = 'all')
        #changed arg pos 1 from objectid to self.origins_identifierfield
        

    def destinations_to_lines(self):
        """
        joins destinations  to lines and adds POINT_X, POINT_Y fields
        """
        if not self.__solve:
            print('run solve first')
            raise TypeError
        descr = arcpy.da.Describe(self.odcost_layer)
        self.lines_path = self.__get_na_layer_path__(descr,'Lines')
        
        self.destinations_path = self.__get_na_layer_path__(descr,'Destinations')
        self.destinations_path_path = pathlib.Path(self.destinations_path)
        self.destinations_path_name = self.destinations_path_path.name
        
        arcpy.AddXY_management(self.destinations_path)
        joins.join_1one1(self.destinations_path, 'ObjectID', self.outgdb, self.lines_path, 'DestinationID', ['Name','POINT_X','POINT_Y'])
        joins.join_1one1(self.destinations,self.destinations_identifierfield, self.outgdb,self.lines_path,f'Name_{self.destinations_path_name}', from_fields = 'all')
        # changed arg pos 1 from objectid to self.destinations_identifierfield


    def multiple_origins(self, outname, outgdb, overwrite = True):
        """"
        Makes a featureclass with one "origin" for every line. Use Dissolve for generating statistics and reduce to one feature.
        outgdb -- string, path to gdb for placeing result
        outname -- string, name of result featureclass
        overwrite -- BOOL, True or False. Defaults to True. Result can be overwriten.
        """
        if not self.__solve:
            print('run solve first')
            raise TypeError
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
            #print(item)
            insertcursor.insertRow(item)


class Route:
    """Makes a arcpy.na.MakeRouteAnalysisLayer

    network -- string, path to network dataset
    outgdb -- string, path to .gdb to place Route


    Methods:
    routepairs -- makes routes based on origins-destinationpairs, and optional via-points
    """

    def __init__(self, network, outgdb, **kwargs):

        def __kvargs_to_full_dict__(valid_RouteAnalysisLayer_parameters, kwargs):
            vals =  {}
            for i in valid_RouteAnalysisLayer_parameters:
                try:
                    vals[i] = kwargs[i]
                except KeyError:
                    vals[i] = None
            return vals

        self.valid_RouteAnalysisLayer_parameters = ['layer_name', 'travel_mode', 'sequence', 'time_of_day', 'time_zone',
                                                    'line_shape', 'accumulate_attributes']
        self.network = network

        ##
        self.network_prj = arcpy.Describe(self.network).spatialReference
        ##

        self.outgdb = outgdb
        arcpy.env.workspace = self.outgdb
        #if kwargs:
        self.given_RouteAnalysisLayer_parameters = __kvargs_to_full_dict__(self.valid_RouteAnalysisLayer_parameters, kwargs)
        self.layer_name = self.given_RouteAnalysisLayer_parameters['layer_name']
        self.travel_mode = self.given_RouteAnalysisLayer_parameters['travel_mode']
        self.time_of_day = self.given_RouteAnalysisLayer_parameters['time_of_day']
        self.time_zone = self.given_RouteAnalysisLayer_parameters['time_zone']
        self.line_shape = self.given_RouteAnalysisLayer_parameters['line_shape']
        self.accumulate_attributes = self.given_RouteAnalysisLayer_parameters['accumulate_attributes']

        ral = arcpy.na.MakeRouteAnalysisLayer(self.network, self.layer_name, self.travel_mode, self.time_of_day,
                                              self.time_zone, self.line_shape, self.accumulate_attributes)

        self.routelayer = ral.getOutput(0)
        self.sublayer_names = arcpy.na.GetNAClassNames(self.routelayer)
        self.stops_layer_name = self.sublayer_names["Stops"]
        self.routes_layer_name = self.sublayer_names["Routes"]

    def routepairs(self, origins, originskey, destinations, destinationskey, result_fc, via=None, viakey=None,
                   overwrite=False):
        """
        origins -- string, path to origins featureclass.
        originskey -- string, fieldname holding key common with destinationkey.
        destinations -- string, path to destinations featureclass.
        destinationskey -- string, fieldname holding key common with originkey
        result_fc, -- string, path to result featureclass.
        via, -- string (optional), path to viapoints featurecalss
        viakey, -- string (optional), fieldname holding key common with origin and destionation
        overwrite, -- BOL (optional), overwrite result_fc if set to True
        """

        arcpy.env.overwriteOutput = overwrite
        # mapping origins and adding
        field_mappings = arcpy.na.NAClassFieldMappings(self.routelayer, self.stops_layer_name)
        field_mappings["RouteName"].mappedFieldName = originskey
        arcpy.na.AddLocations(self.routelayer, self.stops_layer_name, origins,
                              field_mappings, "")  # kwargs for add locations
        # adding via points if any
        if via:
            if not viakey:
                print(f'{via} was given as via-points but no field was spesified as viakey')
                raise ValueError
            print('adding via-points')
            field_mappings = arcpy.na.NAClassFieldMappings(self.routelayer, self.stops_layer_name)
            field_mappings["RouteName"].mappedFieldName = viakey
            arcpy.na.AddLocations(self.routelayer, self.stops_layer_name, via,
                                  field_mappings, "")  # kwargs for add locations
        # mapping destinations
        field_mappings = arcpy.na.NAClassFieldMappings(self.routelayer, self.stops_layer_name)
        field_mappings["RouteName"].mappedFieldName = destinationskey
        arcpy.na.AddLocations(self.routelayer, self.stops_layer_name, destinations,
                              field_mappings, "")  # kwargs for add locations
        try:
            arcpy.na.Solve(self.routelayer)
        except arcpy.ExecuteError as e:
            print (e)
        routes_sublayer = self.routelayer.listLayers(self.routes_layer_name)[0]
        arcpy.management.CopyFeatures(routes_sublayer, result_fc)


def countlines(gdb, linefc, outfc, countfield= 'linecount', overwrite=True):

    """count identical lines in linefc  and return outfc with a field
    (linecount) holding the count of equal lines. Outfc will  be split
    on verticies.

    gdb -- string, path to .gdb where linefc exists
    linefc -- string, name of line featureclass in gdb to count
    outfc -- string, path or name of  output featureclass with count.
    If not path, result is placed in gdb.
    """


    arcpy.env.workspace = gdb
    arcpy.env.overwriteOutput = overwrite

    lines_split = f'{linefc}_split'
    arcpy.SplitLine_management(linefc,lines_split)
    all_lines = [row[0] for row in arcpy.da.SearchCursor(lines_split, 'shape@')]

    counter  = Counter()
    unike = { }

    with arcpy.da.SearchCursor(lines_split,'shape@') as cursor:
        for i, row in (enumerate(cursor)):
            collect = []
            for ii, line in enumerate(all_lines):
                if row[0].equals(line):
                    unike[i] = row[0]
                    counter.update([i])
                    collect.append(ii)
            all_lines = [geom for i, geom in enumerate(all_lines) if i not in collect]

    outfc_p = pathlib.Path(outfc)
    if outfc_p.is_dir():
        print('outfc is dir')
        outpath = outfc_p.parent
        outname = outfc_p.name
    else:
        outpath = gdb
        outname = outfc
    print(outpath, outname)
    arcpy.CreateFeatureclass_management(outpath, outname, 'polyline', spatial_reference= linefc )
    arcpy.AddField_management(os.path.join(outpath, outname), countfield, 'LONG')

    insertcursor = arcpy.da.InsertCursor(outfc, ['shape@', countfield, ])

    for  k,v in unike.items():
        insertcursor.insertRow((v, counter[k]))
    del insertcursor
