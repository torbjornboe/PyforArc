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
    notwanteds = ['OBJECTID', 'Shape', 'SHAPE']
    values = list(fieldmap.values())
    keys = list(fieldmap.keys())
    rest_targetfieldsdict = {f.name: f.type for f in arcpy.ListFields(target) if f.name not in notwanteds + keys}
    rest_appendfieldsdict = {f.name: f.type for f in arcpy.ListFields(target) if f.name not in notwanteds + values}
    rest_appendfieldslist = []
    
    for fname,ftype in rest_appendfieldsdict.items():
        try:
            if rest_targetfieldsdict[fname] ==  ftype: #field exist and of same type
                rest_appendfieldslist.append(fname)
        except KeyError: # field does not exist
            pass

    appends = [row for row in arcpy.da.SearchCursor(appendfc,['shape@']+values+rest_appendfieldslist)]
    insertcursor = arcpy.da.InsertCursor(target,['shape@']+keys)

    for item in appends:
        insertcursor.insertRow(item)

