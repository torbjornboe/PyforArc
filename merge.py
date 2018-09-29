import arcpy

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
    arcpy.CreateFeatureclass_management(gdb,outfc,desc_merge1.shapeType,template=trees, spatial_reference = trees)
    if type(fieldmap) != dict:
        print('fieldmap not dict')
        raise TypeError
    values = list(fieldmap.values())
    keys = list(fieldmap.keys())
    merge1_cursor = arcpy.da.SearchCursor(merge1,['shape@']+keys)
    merge2_cursor = arcpy.da.SearchCursor(merge2,['shape@']+values)
    insertcursor = arcpy.da.InsertCursor(outfc,['shape@']+keys)

    for row in merge1_cursor:
        inserts = [row[0]]
        for index,fields in enumerate(keys,1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)


    for row in merge2_cursor:
        inserts = [row[0]]
        for index,fields in enumerate(values,1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)

    del merge1_cursor
    del merge2_cursor
    del insertcursor




