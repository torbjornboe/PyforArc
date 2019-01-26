import arcpy
import pandas as pd

import addmultiplefields

map_tbl_to_df = {'String':'U', 'Float': 'f', 'Double': 'f', 'Short': 'i', 'Long':'i', 'Date': 'M', 'OID':'i', 'Geometry':'O'}
map_df_to_tbl = {'U': 'String', 'f': 'Double', 'i': 'OID', 'M': 'Date', 'O': 'Geometry'}
#['OID', 'Geometry', 'String', 'Double']
def table_to_dataframe(fc, workspace = None, index = None):
    if workspace:
        arcpy.env.workspace = workspace
        
    fields = [field.name for field in arcpy.ListFields(fc)]
    types = {field.name: field.type for field in arcpy.ListFields(fc)}
    
    if index:
        index = [row[0] for row in arcpy.da.SearchCursor(fc,index)]
        
    data = [list(row) for row in arcpy.da.SearchCursor(fc,fields)]
    df = pd.DataFrame(data, index = index, columns = fields)
    
    for field in fields:
        print(field)
        print(types[field])
        print(map_tbl_to_df[types[field]])
        df[field].astype(map_tbl_to_df[types[field]])
    return df
    

def dataframe_to_featureclass(dataframe, featureclass, geometry, workspace = None, spatial_reference = None):
    if workspace:
        arcpy.env.workspace = workspace
    if spatial_reference:
        try:
            p = pathlib.Path(spatial_reference)
            isdir = p.parent.is_dir()
        except TypeError:
            spatial_reference = arcpy.SpatialReference(spatial_reference)
                    
    arcpy.CreateFeatureclass_management(workspace, featureclass, geometry, spatial_reference = spatial_reference)

    #dt.kind
    #remember to resolve workspace and name for addmultiplefields
    columns = df.columns
    fields = []
    for column in columns:
        pass
	#columns.append((column,df[i].dtype.kind))
	
    addmultiplefields.addmultiplefields(workspace,featureclass,fields)

    icursor = arcpy.da.InsertCursor(featureclass,columns+['shape@'])

    for i,row in df.iterrows():
	icursor.insertRow((row.iloc[:].values))# + geometry. need logic for geometrytype
        

    #df['SHAPE'].loc[:1].values

    
    

    
    

    
    
if __name__ == '__main__':
    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    origins = 'plants'
    df = table_to_dataframe(origins,gdb,'OBJECTID')#'OBJECTID'
    print(df.head())
    print(df.index)
