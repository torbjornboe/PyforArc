import arcpy, pathlib, sys

def join_1one1(from_fc, from_keyfield, to_gdb, to_fc, to_keyfield, from_fields = None):
    """Joines 1:M or 1:1. This tool has no output! from_ denotes that this has to do with the featureclass you are getting values from.
    to_ denotes the featureclass you are joining to. keyfield are the fields the join will be based on. keyfield must be uniqe for from_fc.
    from_fields can be a list containing field name or set to 'all' to transfer all fields exept OBJECTID and Shape.
    """

    arcpy.env.workspace = to_gdb

    if from_fields == None:
        raise ValueError
        print('no value for from_fields, use keywort "all" or tuple')
    if from_fields == 'all':
        print(f'all fields from {from_fc} beeing transferred to {to_fc}')
        ## path = pathlib.Path(from_fc) Pretty cool but not needed. Listfield works without arcpy.env.workspace
        ## arcpy.env.workspace = path.parent
        from_fields = arcpy.ListFields(from_fc)
        print(f'listFields from_fields: {from_fields}')
        from_fields = [(i.name,i.type) for i in from_fields if i.name not in [from_keyfield, 'OBJECTID','ObjectID','Shape','SHAPE']] # from_keyfield 'OBJECTID','ObjectID',
    else:
        if type(from_fields) == str:
            from_fields = from_fields.split(',')
        from_fields = [(i.name,i.type) for i in arcpy.ListFields(from_fc) if i.name in from_fields]


    # add new fields
    all_tofields = {field.name:field.type for field in arcpy.ListFields(to_fc)}
    print (f'all tofields: {all_tofields}')
    all_fromfields = {field.name:field.type for field in arcpy.ListFields(from_fc)}
    print (f'all fromfields: {all_fromfields}')
    keyfield_type_equal = True
    if all_tofields[to_keyfield] != all_fromfields[from_keyfield]:
        keyfield_type_equal = False

    # some code for detecting different fieldtype
    # all_tofields = [field.name for field in all_tofields]
    frompath = pathlib.Path(from_fc)
    fromname = frompath.name # name of form_fc needed below. This will get name even if input is not a path and only filename
    new_fromfields = []
    for field in from_fields:
        if field[0] not in all_tofields:
            try:
                print (f'adding {field} to {to_fc}')
                arcpy.AddField_management(to_fc,field[0],field[1])
                new_fromfields.append(field[0])
            except arcpy.ExecuteError as e:
                print (f'{e}')
                raise arcpy.ExecuteError
        else:
            if field[1] == all_tofields[field[0]]:
                arcpy.AddField_management(to_fc,f'{field[0]}_{fromname}',field[1])
                new_fromfields.append(f'{field[0]}_{fromname}')
                print(f'{field[0]} exists in {to_fc}. Field added as {field[0]}_{fromname}')
                #print (f'{field[0]} of type {field[1]} exists in {to_fc}. Not safe to continue. Please remove field from {to_fc} or rename field in {from_fc}')
                #raise ValueError
            else:
                print(f'{field[0]} exists in {to_fc} but is of type {all_tofields[field[0]]}. Field added as {field[0]}_{fromname}')
                arcpy.AddField_management(to_fc,f'{field[0]}_{fromname}',field[1])
                new_fromfields.append(f'{field[0]}_{fromname}')
                #raise ValueError

    # check that only uniqe values exists in from_keyfield
    from_keys = [i for i in arcpy.da.SearchCursor(from_fc,from_keyfield)]
    if len(from_keys) != len(set(from_keys)):
        print(f'field {from_keyfield} in {from_fc} has non-uniqe values')
        raise ValueError

    # Use list comprehension to build a dictionary from a da SearchCursor
    from_fields = [i[0] for i in from_fields]
    from_fields.insert(0,from_keyfield)

    if keyfield_type_equal:
        valuedict = {r[0]:(r[1:]) for r in arcpy.da.SearchCursor(from_fc, from_fields)}
    else:
        valuedict = {str(r[0]):(r[1:]) for r in arcpy.da.SearchCursor(from_fc, from_fields)}

    print(valuedict)

    from_fields = from_fields[1:] # removing from_keyfield as this field does not exist in to_fc
    print(f'from_fields {from_fields}')
    print(f'joining values from {from_fc} to {to_fc}')
    print(f'new_fromfields: {new_fromfields}')
    print([to_keyfield]+new_fromfields)
    with arcpy.da.UpdateCursor(to_fc, [to_keyfield]+new_fromfields) as cursor: #from_fields has been transferred to to_fc
        for row in cursor:
            # store the joinvalue of the row being updated in a keyvalue variable
            keyvalue = row[0]
            if not keyfield_type_equal:
                keyvalue = str(keyvalue)
            try: # transfer the value stored under the keyValue from the dictionary to the updated field.
                for n,item in enumerate(from_fields,1):
                    row[n] = valuedict[keyvalue][n-1]
                    print(f'row is {valuedict[keyvalue][n-1]}')
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
    fromfields = ['Stasjon']
    join_1one1(fromfc,from_keyfield,togdb,tofc,to_keyfield,from_fields = fromfields)




