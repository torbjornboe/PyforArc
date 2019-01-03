
class Test:
    def __init__(self, a):
        def somedef(a):
            return a + '_abc'
        def add(a):
            return(f'{a}_____')
        self.somdef = somedef
        self.a = a
        #self.a = add(a)
        #print(somedef(a))

    def usedef(self):
        print(self.somdef(self.a))

    
        

    
