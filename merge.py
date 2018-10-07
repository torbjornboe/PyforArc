import arcpy

from addmultiplefields import addmultiplefields 

class BaseValidationError(TypeError):
    pass

class DifferentShapeTypesError(BaseValidationError):
    pass

def merge(gdb,merge1,merge2,fieldmap,outfc,overwrite = False):
    """
    gdb -- workspace gdb
    merge1 -- string, output takes fields and shapeType from this
    merge2 -- string, fields merged according to fieldmap
    fieldmap -- dict, e.g. {field_merge1: field_merge2}
    outfc -- string, output merge
    overwrite -- BOOL
    """
    arcpy.env.workspace = gdb
    if overwrite:
        arcpy.env.overwriteOutput = True
    desc_merge1 = arcpy.Describe(merge1)
    desc_merge2 = arcpy.Describe(merge2)
    if desc_merge1.shapeType != desc_merge2.shapeType:
        raise DifferentShapeTypesError

    if type(fieldmap) != dict:
        print('fieldmap not dict')
        raise TypeError
    
    values = list(fieldmap.values())
    keys = list(fieldmap.keys())
    merge1_fields = [(f.name,f.type) for f in arcpy.LitstFields(merge1) if f not in ['OBJECTID','Shape']]
    merge2_fields = [(f.name,f.type) for f in arcpy.LitstFields(merge2) if f not in ['OBJECTID','Shape']]
    merge2_out = [f for f in merge2_field if f[0] not in values]#fields from merge2 that is not in fieldmap
    merge1_restfields = [f for f in merge1_field if f[0] not in keys]
    keys_type = [f for f in merge1_field if f[0] in keys]
    values_type = [f for f in merge2_field if f[0] in values]
    outfields = merge1_restfields + merge2_out + keys_type + values_type
    arcpy.CreateFeatureclass_management(gdb,outfc, desc_merge1.shapeType, spatial_reference = merge1)
    addmultiplefields(gdb,outfc,outfields)

    merge1_cursor = arcpy.da.SearchCursor(merge1,['shape@'] + merge1_restfields + keys)
    merge2_cursor = arcpy.da.SearchCursor(merge2,['shape@'] + merge2_out + vales)
    
    insertcursor = arcpy.da.InsertCursor(outfc,['shape@'] + merge1_restfields + keys)

    for row in merge1_cursor:
        inserts = [row[0]]
        for index,fields in enumerate(merge1_restfields+keys,1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)
    del insertcursor

    insertcursor = arcpy.da.InsertCursor(outfc,['shape@'] + merge2_out + values)

    for row in merge2_cursor:
        inserts = [row[0]]
        for index,fields in enumerate(merge2_out + values,1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)

    del merge1_cursor
    del merge2_cursor
    del insertcursor




