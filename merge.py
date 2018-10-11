# thrid party imports
import arcpy

# local imports
from addmultiplefields import addmultiplefields


class BaseValidationError(TypeError):
    pass


class DifferentShapeTypesError(BaseValidationError):
    pass


def merge(merge1, merge2, outfc, fieldmap=None, gdb=None, overwrite=False):
    """
    merge merge1 and merge2 to outfc. if gdb is given arcpy.env.workspace 
    is set to this, else full paths are allways needed. All fields are 
    transferred, but use fieldmap to to map fields from merge2 to merge1-fields. 


    gdb -- workspace gdb
    merge1 -- string, output takes fields and shapeType from this
    merge2 -- string, fields merged according to fieldmap
    fieldmap -- dict, e.g. {field_merge1: field_merge2}
    outfc -- string, output merge
    overwrite -- BOOL
    """

    if gdb is not None:
        arcpy.env.workspace = gdb
    if overwrite:
        arcpy.env.overwriteOutput = True
    desc_merge1 = arcpy.Describe(merge1)
    desc_merge2 = arcpy.Describe(merge2)
    if desc_merge1.shapeType != desc_merge2.shapeType:
        raise DifferentShapeTypesError

    if fieldmap:
        if type(fieldmap) != dict:
            print('fieldmap not dict')
            raise TypeError
        values = list(fieldmap.values())
        keys = list(fieldmap.keys())
    else:
        values = []
        keys = []

    merge1_fields = [(f.name, f.type) for f in arcpy.ListFields(
        merge1) if f.name not in ['OBJECTID', 'Shape', 'SHAPE']]
    merge2_fields = [(f.name, f.type) for f in arcpy.ListFields(
        merge2) if f.name not in ['OBJECTID', 'Shape', 'SHAPE']]
    # fields from merge2 that is not in fieldmap
    merge2_restfields = [f for f in merge2_fields if f[0] not in values]
    merge1_restfields = [f for f in merge1_fields if f[0] not in keys]
    keys_type = [f for f in merge1_fields if f[0] in keys]
    values_type = [f for f in merge2_fields if f[0] in values]
    outfields = merge1_restfields + merge2_restfields + keys_type
    arcpy.CreateFeatureclass_management(
        gdb, outfc, desc_merge1.shapeType, spatial_reference=merge1)
    addmultiplefields(gdb, outfc, outfields)

    merge1_restfields = [f[0] for f in merge1_restfields]
    merge1_cursor = arcpy.da.SearchCursor(
        merge1, ['shape@'] + merge1_restfields + keys)
    merge2_restfields = [f[0] for f in merge2_restfields]
    merge2_cursor = arcpy.da.SearchCursor(
        merge2, ['shape@'] + merge2_restfields + values)
    insertcursor = arcpy.da.InsertCursor(
        outfc, ['shape@'] + merge1_restfields + keys)

    for row in merge1_cursor:
        inserts = [row[0]]
        for index, fields in enumerate(merge1_restfields + keys, 1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)
    del insertcursor

    insertcursor = arcpy.da.InsertCursor(
        outfc, ['shape@'] + merge2_restfields + keys)
    for row in merge2_cursor:
        inserts = [row[0]]
        for index, fields in enumerate(merge2_restfields + keys, 1):
            inserts.append(row[index])
        insertcursor.insertRow(inserts)

    del merge1_cursor
    del merge2_cursor
    del insertcursor


if __name__ == '__main__':
    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    plants = 'plants_2'
    trees = 'trees_2'
    outfc = 'vegetation_2_no_fieldmap'
    # fieldmap = {'tree_diam': 'plant_diam', 'tree_type': 'plant_type'}
    merge(trees, plants, outfc, overwrite=True, gdb=gdb)
