import json

import arcpy
import pandas as pd

import addmultiplefields

map_tbl_to_df = {'String':'U', 'Float': 'f', 'Double': 'f', 'Short': 'i', 'Long':'i', 'Integer':'i', 'Date': 'M', 'OID':'i', 'Geometry':'O'}
map_df_to_tbl = {'U': 'String', 'f': 'Float', 'i': 'Long', 'M': 'Date', 'O': 'String'}

def table_to_dataframe(fc, workspace = None, index = None):
    """Esri .gdb table to Pandas dataframe


    fc -- string, path to table\featureclass or just name if workspace is given
    workspace -- string, path to .gdb
    index -- string, name of field to use as index
    return -- object, pandas.DataFrame
    """

    if workspace:
        arcpy.env.workspace = workspace
        
    fields = [field.name for field in arcpy.ListFields(fc)]
    types = {field.name: field.type for field in arcpy.ListFields(fc)}
    #print(types)
    
    if index:
        index = [row[0] for row in arcpy.da.SearchCursor(fc,index)]
        
    data = [list(row) for row in arcpy.da.SearchCursor(fc,fields + ['SHAPE@JSON'])]
    df = pd.DataFrame(data, index = index, columns = fields + ['SHAPE@JSON'])
    
    for field in fields:
        df[field].astype(map_tbl_to_df[types[field]])
    #print(df['SHAPE@JSON'])
    return df
    

def dataframe_to_featureclass(df, featureclass, geometry, workspace, geometrycolumn = 'SHAPE@JSON', overwrite = False):
    """Dataframe containing geometry as SHAPE@JSON json

    df -- pandas.DataFrame, dataframe containing as a ESRI SHAPE@JSON json
    featureclass -- string, name of featureclass
    workspace -- string, path to .gdb
    geometry -- string, <polygon, polyline, point>
    geometrycolumn -- string, columns holding SHAPE@JSON json
    overwrite -- BOOL, <True or False>
    """
    geometry = geometry.lower()
    allowed_geometry = ['polygon','polyline','point']
    if geometry not in allowed_geometry:
        print ('geometry of type {geometry} not recognised. Allowed geometry is: {""", """.join(allowed_geometry)}')
        raise TypeError
    if workspace:
        arcpy.env.workspace = workspace
        arcpy.env.overwriteOutput = overwrite

    # should implement a copy to avoid potential conflict with existing columns
    df['__wkid__'] = df['SHAPE@JSON'].apply(lambda x: json.loads(x)['spatialReference']['wkid'])
    if len(df['__wkid__'].unique()) > 1:
        print('data containing non-uniqe spatial reference')
        raise ValueError
    spatial_reference = arcpy.SpatialReference(df['__wkid__'].unique()[0])
    arcpy.CreateFeatureclass_management(workspace, featureclass, geometry, spatial_reference = spatial_reference)

    #remember to resolve workspace and name for addmultiplefields
    columns = df.columns
    fields = []
    reserved = ['OBJECTID', 'SHAPE',]
    for column in columns:
        if column not in [geometrycolumn]:
            if column.upper() in reserved:
                new_col = f'{column}_df'
                df.rename(columns= {column: new_col}, inplace= True)
                fields.append((new_col,map_df_to_tbl[df[new_col].dtype.kind]))
            else:
                fields.append((column,map_df_to_tbl[df[column].dtype.kind]))
            
            
    addmultiplefields.addmultiplefields(workspace,featureclass,fields)
    fields = [field[0] for field in fields]
    icursor = arcpy.da.InsertCursor(featureclass,fields + ['shape@'])

    for i,row in df[fields].iterrows():
        if geometry == 'point':
            geometrydata = json.loads(df.loc[i,geometrycolumn])
            point = arcpy.Point(geometrydata['x'], geometrydata['y'])
            arc_geometry = [arcpy.PointGeometry(point)]
        if geometry == 'polygon':
            geometrydata = json.loads(df.loc[i,geometrycolumn])
            arc_geometry = []
            for feature in geometrydata['rings']:
                arc_geometry.append(arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in feature])))
        if geometry == 'polyline':
            geometrydata = json.loads(df.loc[i,geometrycolumn])
            arc_geometry = []
            for feature in geometrydata['paths']:
                arc_geometry.append(arcpy.Polyline(arcpy.Array([arcpy.Point(*coords) for coords in feature])))
        nrow = []
        for val in row:
            if type(val) == tuple:
                val = str(val)
            nrow.append(val)
        payload = nrow + arc_geometry
        icursor.insertRow(payload)
