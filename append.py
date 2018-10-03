import arcpy

class BaseValidationError(TypeError):
    pass

class DifferentShapeTypesError(BaseValidationError):
    pass

def append(gdb,target,appendfc,fieldmap):

    arcpy.env.workspace = gdb
    desc_target = arcpy.Describe(target)
    desc_appendfc = arcpy.Describe(appendfc)
    if desc_target.shapeType != desc_appendfc.shapeType:
        raise DifferentShapeTypesError
    if type(fieldmap) != dict:
        print('fieldmap not dict')
        raise TypeError
    values = list(fieldmap.values())
    keys = list(fieldmap.keys())
    appends = [row for row in arcpy.da.SearchCursor(appendfc,['shape@']+values)]
    print (appends)
    insertcursor = arcpy.da.InsertCursor(target,['shape@']+keys)

    for item in appends:
        insertcursor.insertRow(item)


if __name__ == '__main__':
    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    plants = 'plants_1'
    trees = 'trees_1'
    fieldmap = {'tree_diam': 'plant_diam', 'tree_type': 'plant_type'}
    append(gdb,trees,plants,fieldmap)
