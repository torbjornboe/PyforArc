import arcpy

class BaseValidationError(TypeError):
    pass

class DifferentShapeTypesError(BaseValidationError):
    pass

class FieldmapNotDictError(BaseValidationError):
    pass

def append(gdb,target,appendfc,fieldmap):
    """
    This tool has no output! Appends appendfc to target using fieldmap.
    
    gdb -- string, workspace gdb
    target -- string, target fc for appending
    appendfc -- fc to append to target
    fieldmap -- dict, e.g. {field_target: field_appendfc}
    """
    arcpy.env.workspace = gdb
    desc_target = arcpy.Describe(target)
    desc_appendfc = arcpy.Describe(appendfc)
    if desc_target.shapeType != desc_appendfc.shapeType:
        raise DifferentShapeTypesError
    if type(fieldmap) != dict:
        raise FieldmapNotDictError
    values = list(fieldmap.values())
    keys = list(fieldmap.keys())
    appends = [row for row in arcpy.da.SearchCursor(appendfc,['shape@']+values)]
    insertcursor = arcpy.da.InsertCursor(target,['shape@']+keys)

    for item in appends:
        insertcursor.insertRow(item)

