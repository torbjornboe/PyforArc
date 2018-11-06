import arcpy


def od_cost(network, outgdb, origins, destinations, **kwargs):
	search_tolerance = 500
	arcpy.env.overwriteOutput = True
	arcpy.env.workspace = outgdb
	#  output_layer_file = os.path.join(output_dir, layer_name + ".lyrx")
	od_cost = arcpy.na.MakeODCostMatrixAnalysisLayer(network, "testODcostPro")
	odcost_layer = od_cost.getOutput(0)

	sublayer_names = arcpy.na.GetNAClassNames(odcost_layer)
	origins_layer_name = sublayer_names["Origins"]
	destinations_layer_name = sublayer_names["Destinations"]
	
	# test
	print(odcost_layer)
	
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

    # layer_object.saveACopy(output_layer_file)


if __name__ == '__main__':
	nd = r'C:\temp_data\vegnett_RUTEPL_180628.gdb\Route\ERFKPS_ND'
	gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
	origins = 'plants'
	destinations = 'trees'
	od_cost(nd,gdb,origins,destinations)

