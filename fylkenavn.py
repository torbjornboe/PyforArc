import arcpy

def kalkuler_fylke(gdb,fc,kommunenr,updatefield):
    """
    Calculate name of norwegian county a municipal is a member of based on municipal-id.
    This tool has no output!
    gdb -- string. Path to .gdb where featureclass to be calculated recides.
    fc -- string. featureclass to be calculted
    kommunenr -- string. Field of type string or integer, holding municipal id
    updatefield -- string. Field of type string to place result
    """

    
    fylker = {
    '01': 'Østfold',
    '02': 'Akershus',
    '03': 'Oslo',
    '04': 'Hedmark',
    '05': 'Oppland',
    '06': 'Buskerud',
    '07': 'Vestfold',
    '08': 'Telemark',
    '09': 'Aust-Agder',
    '10': 'Vest-Agder',
    '11': 'Rogaland',
    '12': 'Hordaland',
    '14': 'Sogn og Fjordane',
    '15': 'Møre og Romsdal',
    '16': 'Sør-Trøndelag',
    '17': 'Nord-Trøndelag',
    '18': 'Nordland',
    '19': 'Troms',
    '20': 'Finnmark',
    '21': 'Svalbard',
    '22': 'Jan Mayen',
    '50': 'Trøndelag',
    }
    
    arcpy.env.workspace = gdb
    cursor = arcpy.da.UpdateCursor(fc,[kommunenr,updatefield])
    for row in cursor:
        try:
            knr = str(row[0])
            if len(knr) == 3:
                knr = knr.zfill(4)
            row[1] = fylker[knr[:2]]
        except KeyError:
            row[1] = None
        cursor.updateRow(row)
    

