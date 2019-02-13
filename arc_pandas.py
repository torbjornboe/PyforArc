import arcpy
import pandas as pd
import pathlib

import addmultiplefields

map_tbl_to_df = {'String':'U', 'Float': 'f', 'Double': 'f', 'Short': 'i', 'Long':'i', 'Date': 'M', 'OID':'i', 'Geometry':'O'}
map_df_to_tbl = {'U': 'String', 'f': 'Float', 'i': 'Long', 'M': 'Date', 'O': 'String'}
#['OID', 'Geometry', 'String', 'Double']
def table_to_dataframe(fc, workspace = None, index = None):
    if workspace:
        arcpy.env.workspace = workspace
        
    fields = [field.name for field in arcpy.ListFields(fc)]
    types = {field.name: field.type for field in arcpy.ListFields(fc)}
    
    if index:
        index = [row[0] for row in arcpy.da.SearchCursor(fc,index)]
        
    data = [list(row) for row in arcpy.da.SearchCursor(fc,fields + ['SHAPE@JSON'])]
    df = pd.DataFrame(data, index = index, columns = fields + ['SHAPE@JSON'])
    
    for field in fields:
        df[field].astype(map_tbl_to_df[types[field]])
    print(df['SHAPE@JSON'])
    return df
    

def dataframe_to_featureclass(df, featureclass, geometry, geometrycolumn = 'SHAPE', workspace = None, spatial_reference = None, overwrite = True):
    geometry = geometry.lower()
    allowed_geometry = ['polygon','polyline','point']
    if geometry not in allowed_geometry:
        print ('geometry of type {geometry} not recognised. Allowed geometry is: {""", """.join(allowed_geometry)}')
        raise TypeError
    if workspace:
        arcpy.env.workspace = workspace
        arcpy.env.overwriteOutput = overwrite
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
    #new_columns = []
    reserved = ['OBJECTID', 'SHAPE',]
    for column in columns:
        if column.upper() in reserved:
            fields.append((f'{column}_',map_df_to_tbl[df[column].dtype.kind]))# adding underscore
            # new_columns.append(column)
        else:
            fields.append((column,map_df_to_tbl[df[column].dtype.kind]))
            
            
    addmultiplefields.addmultiplefields(workspace,featureclass,fields)
    fields = [field[0] for field in fields]
    #print(fields)
    icursor = arcpy.da.InsertCursor(featureclass,fields + ['shape@'])#obs. not working now
    
    #print(columns)
    #df = df[new_columns]
    for i,row in df.iterrows():
        if geometry == 'point':
            point = arcpy.Point(row[geometrycolumn][0], row[geometrycolumn][1])
            #print(point)
            arc_geometry = arcpy.PointGeometry(point)
        if geometry == 'polygon':
            print(row[geometrycolumn])
            array = arcpy.Array(row[geometrycolumn])#possibly need to go innto tuple
            # arc_geometry = arcpy.Polygon(array)
            arc_geometry = row['shape@']
        if geometry == 'polyline':
            array = arcpy.Array(row[geometrycolumn])#needs testing.
            arc_geometry = arcpy.Polyline(array)
        nrow = []
        for val in row:
            if type(val) == tuple:
                val = str(val)
                print(val)
            nrow.append(val)
        #payload = list(row.values) + [arc_geometry]
        payload = nrow + [arc_geometry]
        print(payload)
        print(type(payload))
        icursor.insertRow(payload)
            
            
        #icursor.insertRow((row.iloc[:].values))# + geometry. need logic for geometrytype

    
    

    
    

    
    
if __name__ == '__main__':
    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    origins = 'plants_poly'
    df = table_to_dataframe(origins,gdb,'OBJECTID')#'OBJECTID'
##    print(df.head())
##    print(df.index)
    df['superdiam'] = df['plant_diam'] * 5
    df.to_csv(r'C:\temp_data\df_to_poly2.csv')
    #dataframe_to_featureclass(df, 'df_to_fc_poly2', 'POLYGON', workspace = gdb, spatial_reference = 25832)
