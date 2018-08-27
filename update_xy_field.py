import arcpy

def update_xy_field(workspace,fc,xfield,yfield):
    """updates point features x and y to designated fields, using fc's current CS"""
    arcpy.env.workspace = workspace
    errorcount = 0
    with arcpy.da.UpdateCursor(fc,['SHAPE@X','SHAPE@Y',xfield,yfield]) as cursor:
        for row in cursor:
            try:
                row[2] = row[0] # xfield = SHAPE@X
                row[3] = row[1] # yfield = SHAPE@Y
                cursor.updateRow(row)
            except RuntimeError as e:
                errorcount += 1
                print(f'{e}')
        print(f'errorcount: {errorcount}')


def convert_and_update_xyfield(workspace,fc,xfield,yfield,to_cs,transformationname = None):
    """updates designated x and y fields with coordinates, reprojecting current cs to to_cs. to_cs = .prj or cs name or factory code (wkid)."""
    # http://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-classes/pdf/geographic_coordinate_systems.pdf
    # http://desktop.arcgis.com/en/arcmap/latest/map/projections/pdf/geographic_transformations.pdf
    
    arcpy.env.workspace = workspace
    errorcount = 0
    to_cs = arcpy.SpatialReference(to_cs)
    with arcpy.da.UpdateCursor(fc,['SHAPE@',xfield,yfield]) as cursor:
        for row in cursor:
            try:
                if transformationname:
                    new_cs = row[0].projectAs(to_cs,transformationname)
                else:
                    new_cs = row[0].projectAs(to_cs)
                row[1] = new_cs.firstPoint.X # xfield = SHAPE@X
                row[2] = new_cs.firstPoint.Y # yfield = SHAPE@Y
                cursor.updateRow(row)
            except RuntimeError as e:
                errorcount += 1
                print(f'{e}')
            except AttributeError as e:
                errorcount += 1
                print(f'{e}')
        print(f'errorcount: {errorcount}')
            
    
if __name__ == '__main__':
    wsp = r'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb'
    tbl = 'Austevoll_Innpendling_Busette'
    x = 'Bosted_x'
    y = 'Bosted_y'
    trans = '1149'
    tocs = 25832

convert_and_update_xyfield(wsp,tbl,x,y,tocs)
