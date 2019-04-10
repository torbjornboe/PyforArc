if __name__ == '__main__':

    fromfc = r'C:\Users\torboe_\Documents\ArcGIS\Projects\DefaultProject\DefaultProject.gdb\politi'
    fromfieldlist = "all"
    togdb = r'C:\Users\torboe_\Documents\ArcGIS\Projects\DefaultProject\DefaultProject.gdb'
    tofc = 'skurk'
    to_keyfield = 'keyField'
    from_keyfield = 'key'
    fromfields = ['Stasjon']
    join_1one1(fromfc,from_keyfield,togdb,tofc,to_keyfield,from_fields = fromfields)
