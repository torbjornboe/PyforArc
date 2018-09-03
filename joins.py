import arcpy, pathlib, sys

def join_1one1(from_fc, from_keyfield, to_gdb, to_fc, to_keyfield, from_fields = None):
    """Joines 1:M or 1:1. 'to_fc will' be changed. from_ denotes that this has to to with the featureclass you are getting values from. to_ denotes the featureclass you are joining to. keyfield are the fields the join will be based on. keyfield must be uniqe for from_fc.
    from_fields can be a list of tuples containing field name and type or set to 'all' to transfer all fields exept OBJECTID and Shape.
    """

    if from_fields == None:
        raise ValueError
        print('no value for from_fields, use keywort "all" or tuple')
    if from_fields == 'all':
        print(f'all fields from {from_fc} beeing transferred to {to_fc}')
        ## path = pathlib.Path(from_fc) Pretty cool but not needed. Listfield works without arcpy.env.workspace
        ## arcpy.env.workspace = path.parent
        from_fields = arcpy.ListFields(from_fc)
        from_fields = [(i.name,i.type) for i in from_fields if i.name not in [from_keyfield,'OBJECTID','Shape']]


    # add new fields
    arcpy.env.workspace = to_gdb
    allfields = arcpy.ListFields(to_fc)
    allfields = [field.name for field in allfields]
    for field in from_fields:
        if field[0] not in allfields:
            try:
                print (f'adding {field} to {to_fc}')
                arcpy.AddField_management(to_fc,field[0],field[1])
            except arcpy.ExecuteError as e:
                print (f'{e} Exiting script')
                sys.exit()

    # Use list comprehension to build a dictionary from a da SearchCursor
    from_fields = [i[0] for i in from_fields]
    from_fields.insert(0,from_keyfield)
    valuedict = {r[0]:(r[1:]) for r in arcpy.da.SearchCursor(from_fc, from_fields)}

    from_fields = from_fields[1:] # removing from_keyfield as this field does not exist in to_fc
    with arcpy.da.UpdateCursor(to_fc, [to_keyfield]+from_fields) as cursor: #from_fields has been transferred to to_fc
        for row in cursor:
            # store the joinvalue of the row being updated in a keyvalue variable
            keyvalue = row[0]
            try: # transfer the value stored under the keyValue from the dictionary to the updated field.
                for n,item in enumerate(from_fields,1):
                    row[n] = valuedict[keyvalue][n-1]
                cursor.updateRow(row)
            except KeyError:
                print('keyerror')
                pass

    del valuedict



if __name__ == '__main__':

    fromfc = r'C:\Users\torboe_\Documents\ArcGIS\Projects\DefaultProject\DefaultProject.gdb\politi'
    fromfieldlist = "all"
    togdb = r'C:\Users\torboe_\Documents\ArcGIS\Projects\DefaultProject\DefaultProject.gdb'
    tofc = 'skurk'
    to_keyfield = 'keyField'
    from_keyfield = 'key'

    join_1one1(fromfc,from_keyfield,togdb,tofc,to_keyfield,from_fields = 'all')




