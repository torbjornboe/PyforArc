import arcpy
import collections as col

def floatfields(gdb,fc,fromto):
    """gdb used as workspace, fc is the featureclass,\
from to is a dict where key = fromtextfield, value = tofloatfield"""
    arcpy.env.workspace(gdb)
    addfields = list(fromto.values())
    count = col.Counter(addfields)
    typeerrors = col.Counter()
    

    if max(list(col.values())) > 1:
        print(f'fields {addfields} seems to have duplicates')
        raise ValueError

    for f in addfields:
        arcpy.AddField_management(fc,f,'FLOAT')

    for k,v in fromto:
        with arcpy.da.UpdateCursor(fc,[k,v]) as cursor:
            for row in cursor:
                try:
                    row[1] = float(row[0])
                except TypeError:
                    typeerrors.update([v])
                    pass
                cursor.updateRow(row)
      
    print(f'typeerrors for each field: {typeerrors}')
    
