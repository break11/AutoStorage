class Base1:
    def __init__(self, name = "Base1"):
        print ("Base1 init")
        self.name = name

class Base2:
    def __init__(self, name = "Base2"):
        print ("Base2 init")
        self.name = name

class Child1(Base1, Base2):
    # pass
    # def __init__(self):
    #     pass
    def __init__(self):
        super (Base1, self).__init__()
        # for base_class in Child1.__bases__:
        #     base_class.__init__(self)
        #     print (self.name)

    def names(self):
        print (super(Base1, self).name, super(Base2, self).name)


c = Child1()

c.names()