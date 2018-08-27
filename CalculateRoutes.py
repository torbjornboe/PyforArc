import os,csv,json,sys,shutil,time,requests,arcpy #obs can not use arcpy here
from collections import Counter

def route(start_x,start_y,stop_x,stop_y):
    url = 'http://kart.hfk.no/arcgis/rest/services/Networks/Vegnett_Bil/NAServer/Route/solve?stops={start_x}%2C{start_y}%3B%0D%0A{stop_x}%2C{stop_y}&barriers=&polylineBarriers=&polygonBarriers=&outSR=&ignoreInvalidLocations=true&accumulateAttributeNames=Length&impedanceAttributeName=Minutes&restrictionAttributeNames=Oneway&attributeParameterValues=&restrictUTurns=esriNFSBAllowBacktrack&useHierarchy=false&returnDirections=false&returnRoutes=true&returnStops=false&returnBarriers=false&returnPolylineBarriers=false&returnPolygonBarriers=false&directionsLanguage=en&directionsStyleName=&outputLines=esriNAOutputLineNone&findBestSequence=false&preserveFirstStop=true&preserveLastStop=true&useTimeWindows=false&startTime=0&startTimeIsUTC=false&outputGeometryPrecision=&outputGeometryPrecisionUnits=esriDecimalDegrees&directionsOutputType=esriDOTComplete&directionsTimeAttributeName=&directionsLengthUnits=esriNAUMeters&returnZ=false&travelMode=&f=pjson'.format(start_x=start_x,start_y=start_y,stop_x=stop_x,stop_y=stop_y)
    r = requests.get(url)
    r.raise_for_status()
    routedata = r.json()#object_pairs_hook=OrderedDict
    returndata = {}
##    print url
##    print routedata
    try:
        returndata['length'] = routedata['routes']['features'][0]['attributes']['Total_Length']
        returndata['minutes'] = routedata['routes']['features'][0]['attributes']['Total_Minutes']
    except KeyError:
        try:
            returndata['error']=routedata['error']['message']
        except KeyError:
            returndata['error']='Unknown error'
    except ValueError:
        returndata['error']='ValueError'
    return returndata


fc = r'L:\AUD\AUD Prosjekter\Kommunane\Pendlingsanalyse for Austevoll\Geocode\Pendlingsanalyse.gdb\Austevoll_Innpendling_Busette'
#fc = 'C:\\temp\\Geokoding og reisetid.gdb\\Testdata'
fields=['Bosted_x','Bosted_y','Bedrift_x','Bedrift_y','Length','Minutes','DistError']
with arcpy.da.UpdateCursor(fc,fields) as cursor:
    for row in cursor:
        thisroute = route(row[0],row[1],row[2],row[3])
        try:
            row[4] = thisroute['length']
            row[5] = thisroute['minutes']
        except KeyError:
            row[6] = thisroute['error']
        cursor.updateRow(row)
            
            
        
        
