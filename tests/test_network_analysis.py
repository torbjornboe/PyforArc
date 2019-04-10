from network_analysis import Od_cost

if __name__ == '__main__':
    nd = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\test_odcost.gdb\test_na\test_na_ND'
    gdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\testdata.gdb'
    origins = 'plants'
    destinations = 'trees'
    odcost = Od_cost(nd,gdb,line_shape = 'STRAIGHT_LINES', travel_mode = 'walktime', cutoff = 100, layer_name = 'testname')
    odcost.add_origins(origins,'OBJECTID',500)
    odcost.add_destinations(destinations,'OBJECTID',500)
    odcost.solve()
    odcost.origins_to_lines()
    odcost.destinations_to_lines()
    odcost.multiple_origins('multipleorigins2',gdb)

if __name__ == '__main__':
    resultgdb = r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\test_df\routecount.gdb'
    nd = r'C:\temp_data\vegnett_RUTEPL_181214.gdb\Route\ERFKPS_ND'
    resultfile = 'routelines' # r'C:\Users\torbjorn.boe\Google Drive\Python\PyforArc\tests\test_df\routecount.gdb\routelines'
    origins = r'C:\Users\torbjorn.boe\Google Drive\Python\AVdemo\geocoded.gdb\Bosted'
    destinations = r'C:\Users\torbjorn.boe\Google Drive\Python\AVdemo\geocoded.gdb\Arbeidssted'
    countedlines = 'countedlines'# os.path.join(resultgdb,'countedlines')
    # routelines = 'routelines'
    unikid = 'UnikID'
    route = Route(nd, resultgdb)
    route.routepairs(origins, unikid, destinations, unikid, resultfile, overwrite=True)
    countlines(resultgdb, resultfile, countedlines, 'countedlines', overwrite=True)