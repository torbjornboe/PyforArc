# std lib imports
import logging

# thrid party imports
import arcpy

# local imports
from addmultiplefields import addmultiplefields

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
    # addmultiplefields(gdb, target, outfields)

    appends = [row for row in arcpy.da.SearchCursor(appendfc,['shape@']+values+rest_appendfieldslist)]
    insertcursor = arcpy.da.InsertCursor(target,['shape@']+keys+rest_appendfieldslist)

    for item in appends:
        insertcursor.insertRow(item)


if __name__ == '__main__':

    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    # logger = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\log.txt'
    plants = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb\plants_poly_append'
    trees = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb\trees_poly_append'
    #outfc = 'vegetation_2_testlog'
    fieldmap = {'tree_diam': 'plant_diam', 'tree_type': 'plant_type'}
    append(gdb,trees, plants,fieldmap)
