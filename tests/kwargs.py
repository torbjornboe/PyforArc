def kvargs(req,**kwargs):
    def somefunk(req,name = '', car = '', funk = ''):
        print(name, car, funk)
    if kwargs:
        keylist = ['name','car','funk']
        vals =  {}
        for i in keylist:
            if i not in kwargs:
                vals[i] = None
            else:
                vals[i] = kwargs[i]
    somefunk(req,name = vals['name'], car = vals['car'], funk = vals['funk'])
        

d = {'name':'yooha','car':'lada'}

kvargs(d,name='some',car='lada')
