import arcpy, pathlib

def join_1one1(from_fc, joinfromfield, from_fieldlist, to_gdb, to_fc, jointofield):
    """from_fieldlist -> tuples containing field name and type. joinfromfield = string, unike values matching jointofield. \
        jointofield = string, field to join on"""

    if from_fieldlist == 'all':
##        path = pathlib.Path(from_fc) Pretty cool but not needed. Listfield works without arcpy.env.workspace
##        arcpy.env.workspace = path.parent
        arcpy.ListFields(from_fc)
#make new fields
    arcpy.env.workspace = to_gdb
    allfields = arcpy.ListFields(to_fc)
    allfields = [field.name for field in allfields]
    for field in from_fieldlist:
        if field[0] not in allfields:
            print (f'adding {field} to {to_fc}')
            arcpy.AddField_management(to_fc,field[0],field[1])#change to take fieldtype from from_fc?

# Use list comprehension to build a dictionary from a da SearchCursor
    
    from_fieldlist = [i[0] for i in from_fieldlist]
    from_fieldlist.insert(0,joinfromfield)
    valuedict = {r[0]:(r[1:]) for r in arcpy.da.SearchCursor(from_fc, from_fieldlist)}
    print(from_fieldlist)
    
    print(valuedict)
    from_fieldlist = from_fieldlist[1:]
    with arcpy.da.UpdateCursor(to_fc, [jointofield]+from_fieldlist) as cursor:
        for row in cursor:
            # store the Join value of the row being updated in a keyValue variable
            keyvalue = row[0]
             # verify that the keyValue is in the Dictionary
            if keyvalue in valuedict:
                 # transfer the value stored under the keyValue from the dictionary to the updated field.
                for n,item in enumerate(from_fieldlist,1):
                    row[n] = valuedict[keyvalue][n-1]
                cursor.updateRow(row)

    del valuedict



if __name__ == '__main__':

    fromfc = r'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb\Austevoll_Innpendling_Arbeidsplass'
    fromfieldlist = [('Bedrift_x','DOUBLE'),('Bedrift_y','DOUBLE')]
    togdb = R'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb'
    tofc = 'Austevoll_Innpendling_Busette'
    jointofield = 'UnikID'
    joinfromfield = 'UnikID'

    
    join_1one1(fromfc, joinfromfield, fromfieldlist, togdb, tofc, jointofield)

