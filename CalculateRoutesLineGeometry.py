import os,csv,json,sys,shutil,time,requests,arcpy #obs can not use arcpy here
from collections import Counter

def route(start_x,start_y,stop_x,stop_y):
    url = 'http://kart.hfk.no/arcgis/rest/services/Networks/Vegnett_Bil/NAServer/Route/solve?stops={start_x}%2C{start_y}%3B%0D%0A{stop_x}%2C{stop_y}&barriers=&polylineBarriers=&polygonBarriers=&outSR=&ignoreInvalidLocations=true&accumulateAttributeNames=Length&impedanceAttributeName=Minutes&restrictionAttributeNames=Oneway&attributeParameterValues=&restrictUTurns=esriNFSBAllowBacktrack&useHierarchy=false&returnDirections=false&returnRoutes=true&returnStops=false&returnBarriers=false&returnPolylineBarriers=false&returnPolygonBarriers=false&directionsLanguage=en&directionsStyleName=&outputLines=esriNAOutputLineTrueShapeWithMeasure&findBestSequence=false&preserveFirstStop=true&preserveLastStop=true&useTimeWindows=false&startTime=0&startTimeIsUTC=false&outputGeometryPrecision=&outputGeometryPrecisionUnits=esriDecimalDegrees&directionsOutputType=esriDOTComplete&directionsTimeAttributeName=&directionsLengthUnits=esriNAUMeters&returnZ=false&travelMode=&f=pjson'.format(start_x=start_x,start_y=start_y,stop_x=stop_x,stop_y=stop_y)
    r = requests.get(url)
    r.raise_for_status()
    routedata = r.json()#object_pairs_hook=OrderedDict
    returndata = {}

    try:
        returndata['length'] = routedata['routes']['features'][0]['attributes']['Total_Length']
        returndata['minutes'] = routedata['routes']['features'][0]['attributes']['Total_Minutes']
        returndata['geometry'] = routedata['routes']['features'][0]['geometry']['paths']
    except KeyError:
        try:
            returndata['error']=routedata['error']['message']
        except KeyError:
            returndata['error']='Unknown error'
    except ValueError:
        returndata['error']='ValueError'
    return returndata

def arcpypoints(path):
    points = []
    for array in path[0]:#obs magic number. Needs attention
        arcpypoint = arcpy.Point(array[0],array[1])
        points.append(arcpypoint)
    return points

def has_content(fc):
    with arcpy.da.SearchCursor(fc,'OBJECTID') as cursor:
        try:
            cursor.next()
            print ('has content')
            return True
        except StopIteration:
            return False

starttid = datetime.datetime.now()
print(starttid)

geocoded_fc = r'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb\AustevollUt_Pendling_Bosatte'
lines = r'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb\AustevollUt_Pendling_lines'
fields=['Bosted_x','Bosted_y','Forretning_x','Forretning_y','UnikID']

if has_content(lines):
    sys.exit('{} has content'.format(lines))
print('no content, ready to continue')

with arcpy.da.SearchCursor(geocoded_fc,fields) as cursor:
    insertcursor = arcpy.da.InsertCursor(lines, ['Length','Minutes','UnikID','SHAPE@'])
    for row in cursor:
        thisroute = route(row[0],row[1],row[2],row[3])
        try:
            thisdata = {'unikid':row[4],'length':thisroute['length'],'minutes':thisroute['minutes'],}
            try:
                #thispoit = arcpypoints(thisroute['geometry'])
                thisdata['point'] = arcpypoints(thisroute['geometry'])
            except IndexError:
                pass
        except KeyError:
            thisdata =  {'unikid':row[4],'error':thisroute['error']}
        try:
            array = arcpy.Array(thisdata['point'])
            polyline = arcpy.Polyline(array)
            insertcursor.insertRow((thisdata['length'],thisdata['minutes'],thisdata['unikid'],polyline))
        except KeyError:
            pass
del insertcursor

sluttid = datetime.datetime.now()
brukttid = sluttid - starttid
print(brukttid)
        
