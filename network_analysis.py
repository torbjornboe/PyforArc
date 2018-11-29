import arcpy

import joins

import pathlib

import os

def od_cost(network, outgdb, origins, destinations, **kwargs):
def get_na_layer_path(descr,alias):
        for item in descr['children']:
    try:
                        if item['aliasName'] == alias:
                                return item['dataElement']['catalogPath']
                except KeyError:
                        print('make a base validataion class')

search_tolerance = 500
arcpy.env.overwriteOutput = True
arcpy.env.workspace = outgdb
#  output_layer_file = os.path.join(output_dir, layer_name + ".lyrx")
od_cost = arcpy.na.MakeODCostMatrixAnalysisLayer(network, "testODcostPro")
odcost_layer = od_cost.getOutput(0)

sublayer_names = arcpy.na.GetNAClassNames(odcost_layer)
origins_layer_name = sublayer_names["Origins"]
destinations_layer_name = sublayer_names["Destinations"]

# arcpy.da.Describe(odcost_layer)
#'dataElement': {
#		'catalogPath': 'C:\\Users\\torbjorn.boe\\Google Drive\\Python\\PyforArc\\tests\\testdata.gdb\\ODCostMatrix2\\Origins2',
#		'FIDSet': None,
#		'aliasName': 'Origins',
#		'areaFieldName': '',
#		'baseName': 'Origins2',

# test slutt

field_mappings = arcpy.na.NAClassFieldMappings(odcost_layer,
                                                origins_layer_name)
field_mappings["Name"].mappedFieldName = "OBJECTID"
arcpy.na.AddLocations(odcost_layer, origins_layer_name, origins, field_mappings,
                  search_tolerance)

field_mappings = arcpy.na.NAClassFieldMappings(odcost_layer,
                                                destinations_layer_name)
field_mappings["Name"].mappedFieldName = "OBJECTID"
arcpy.na.AddLocations(odcost_layer, destinations_layer_name, destinations,
                  field_mappings, search_tolerance)

arcpy.na.Solve(odcost_layer)

descr = arcpy.da.Describe(odcost_layer)
origings_path = get_na_layer_path(descr,'Origins')
origings_path_path = pathlib.Path(origings_path)
origings_path_name = origings_path_path.name

destinations_path = get_na_layer_path(descr,'Destinations')
destinations_path_path = pathlib.Path(destinations_path)
destinations_path_name = destinations_path_path.name

lines_path = get_na_layer_path(descr,'Lines')
arcpy.AddXY_management(origings_path)
arcpy.AddXY_management(destinations_path)

print(origings_path, destinations_path, lines_path)
joins.join_1one1(origings_path, 'ObjectID', outgdb, lines_path, 'OriginID', ['Name','POINT_X','POINT_X'])
joins.join_1one1(destinations_path, 'ObjectID', outgdb, lines_path, 'DestinationID', ['Name','POINT_X','POINT_X'])
joins.join_1one1(origins,'OBJECTID',outgdb,lines_path,f'Name_{origings_path_name}', from_fields = 'all')
joins.join_1one1(destinations,'OBJECTID',outgdb,lines_path,f'Name_{destinations_path_name}', from_fields = 'all')


    # layer_object.saveACopy(output_layer_file)


if __name__ == '__main__':
	nd = r'C:\temp_data\vegnett_RUTEPL_180628.gdb\Route\ERFKPS_ND'
	gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
	origins = 'plants'
	destinations = 'trees'
	od_cost(nd,gdb,origins,destinations,)

