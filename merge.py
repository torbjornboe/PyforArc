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

class FieldmapTypeError(BaseValidationError):
    pass


def merge(merge1, merge2, outfc, gdb, fieldmap=None, overwrite=False, logto = None):
    """
    merge merge1 and merge2 to outfc. merge1 and merge2 will be searched for in gdb
    if not full path is given. All fields are transferred if not mapped in fieldmap.
    Use fieldmap to to map fields from merge2 to merge1-fields. If overwrite is set
    outfc will be overwritten if existing. Use logto to log to textfile


    gdb -- workspace gdb
    merge1 -- string, output takes fields and shapeType from this
    merge2 -- string, fields merged according to fieldmap
    fieldmap -- dict, e.g. {field_merge1: field_merge2}
    outfc -- string, output merge
    overwrite -- BOOL
    logto -- string, path to logfile (.txt), mode append
    """
    
    if logto:
        logging.basicConfig(filename=logto, filemode='a', level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.info(f'merging {merge1} and {merge2}')
    if gdb is not None:
        arcpy.env.workspace = gdb
        logging.info(f'env.workspace set to {gdb}')
    if overwrite:
        arcpy.env.overwriteOutput = True
    logging.info(f'overwrite {overwrite}')
    desc_merge1 = arcpy.Describe(merge1)
    desc_merge2 = arcpy.Describe(merge2)
    if desc_merge1.shapeType != desc_merge2.shapeType:
        logging.warning('DifferentShapeTypesError')
        raise DifferentShapeTypesError

    if fieldmap:
        logging.info('fieldmap given as {fieldmap}')
        if type(fieldmap) != dict:
            logging.warning('fieldmap not dict: FieldmapTypeError')
            raise FieldmapTypeError
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
    logging.info(f'outfields: {outfields}')
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

    logging.info(f'merge done')
    del merge1_cursor
    del merge2_cursor
    del insertcursor


