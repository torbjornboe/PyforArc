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
