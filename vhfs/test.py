##register = {}

##SQL_FILTER, RETURN_DIRS = range(2)
##def op_type(operation_type):
    ##def test(f):
        ##register[f.func_name] = operation_type
        ##return f
    ##return test
    

##class Test:

    ##@op_type(SQL_FILTER)
    ##def test1(self):
        ##print 'test1 : ble'



##print '==========='
##t = Test()
##t.test1()

##print register
##pc = PathContext()
##pc.ble = 'spoko'
##pc.ble2 = 'spoko'
##print pc

##class Test:
    ##def __init__(self):
        ##if self.ble == None:
            ##print 'spoko'


##Test()


##def test():
    ##import sys
    ##print sys._getframe(2).f_code.co_name
    ##print sys._getframe(1).f_code.co_name

##def test2():
    ##test()

##test2()

#class Test(object):

    #def __init__(self):
        #self.__x = 0

    #def __get_x(self):
        #return self.__x

    #def __set_x(self, value):
        #self.__x = value

    #x = property(__get_x)
        
#class TestExt(Test):

    #def __init__(self):
        #super(TestExt, self).__init__()

    #def __get_x(self):
        #return 'ble'

    #x = property(__get_x)

    #def print_mro(self):
        #print cls.__mro__
    
#class TestThird(TestExt, Test):

    #def __init__(self):
        #super(Test, self).__init__()

    

##a = TestExt()
##a.print_mro()
##a.test()

#a = Test()
#print a.x
##a.x = 'raz'
#print hasattr(a, 'x')

#a = TestExt()
#print a.x

#class Test:
    #def __init__(self):
        #self._nevermind()

    #def _nevermind(self):
        #print 'test nevermind'
        #t = Test.Test2()
        #t._nevermind()

    #class Test2:

        #def __init__(self):
            #Test.__init__(self)

        #def _nevermind(self):
            #print 'test2 nevermind'



#class Test(object):

    #def __setattr__(self, item, val):
        #print '%s %s ' % (str(item), str(val))
        #return object.__setattr__(self, item, val)

    #def allow_all():
        #return True

    #def test(self):
        #return filter(None, range(10))

#t = Test()
#t.test()
#setattr(t, 'ble', 'bli')
#print t.ble

#from nodes import *

#class NodeList(list):

    #def __init__(self, l = [], parent = None):
        #for item in l:
            #self.append(item)
        #self.parent = parent

    #def __str__(self):
        #prepare = [str(i) for i in self]
        #return str(prepare)

    #def __prepare_value(self, value):
        #if (not isinstance(value, Node) and value <> None):
            #value = ValueNode(value)
            #value.parent = self.parent
        #return value

    #def __setitem__(self, i, value):
        #return super(NodeList, self).__setitem__(i, self.__prepare_value(value))

    #def __setslice__(self, i, j, y):
        #prepared = NodeList(y)
        #return super(NodeList, self).__setslice__(i, j, prepared)
        

    #def __iadd__(self, y):
        #prepared = NodeList(y)
        #return super(NodeList, self).__iadd__(i, j, prepared)

    #def __add__(self, y):
        #out = []
        #out.extend(self)
        #out.extend(NodeList(y))
        #return out

    #def append(self, value):
        #return super(NodeList, self).append(self.__prepare_value(value))

    #def extend(self, y):
        #prepared = NodeList(y)
        #return super(NodeList, self).extend(prepared)

    #def insert(self, i, item):
        #return super(NodeList, self).insert(i, self.__prepare_value(item))

#l = NodeList()
#print l
#l.append(0)
#l[0] = 1

#registry = {}

#class SemanticEnum:
    #UNKNOWN            = 0
    #FILE_RESULT_FILTER = 1
    #SQL_FILTER         = 2
    #DIRENTRY_GENERATOR = 3
    #DIRENTRY_FILTER    = 4

#def deco(semantic_indicator = SemanticEnum.UNKNOWN):
    #decorator_name = 'semantic_' + str(semantic_indicator)
    #exec('''
#def %s(f):
    #import sys
    #import re
    #i = 1
    #trace = []
    #trace.insert(0, f.func_name)
    #while True:
        #stair = sys._getframe(i).f_code.co_name
        #if re.search("module", stair):
            #break
        #trace.insert(0, stair)
        #i += 1
    #func_name = ".".join(trace)
    #registry[func_name] = %s
    #return staticmethod(f)
#''' % (decorator_name, semantic_indicator))
    #return eval(decorator_name)

#class Test(object):

    #SQL_FILTER = 01

    #def __init__(self):
        #print Test.SQL_FILTER
        #Test.Test2()

    #class Public:

        #@deco(SemanticEnum.FILE_RESULT_FILTER)
        #def bla():
            #print 'ble'

        #class Class:

            #@deco(SemanticEnum.FILE_RESULT_FILTER)
            #def example():
                #pass
            

    #class Test2:
        #def __init__(self):
            #Test.Public.bla()

#Test()
#Test.Public.bla()
#print registry

#def switcher(a, b):
    #skeleton = '''
#def set_%(first)s(self, val):
    #self._%(first)s = val
    #self._%(second)s = not val

#def get_%(first)s(self):
    #return self._%(first)s

#def is_%(first)s(self):
    #return self._%(first)s\n'''

    #out = skeleton % {'first' : a, 'second' : b}
    #out += skeleton % {'first' : b, 'second' : a}
    #skeleton = '%(first)s = property(get_%(first)s, set_%(first)s)\n'
    #out += skeleton % {'first' : a}
    #out += skeleton % {'first' : b}
    #exec out
    #print out



#class Test:
    #def __init__(self):
        #self._public = True
        #self._private = False
        #self.classmethod = False
        #pass

    #switcher('public', 'private')

#t = Test()
#print t.public
#print t.private
#print dir(t)

#class SuperTest(object):
    #def __init__(self):
        #print "superTest"

#class SuperTest2(object):
    #def __init__(self):
        #print "superTest2"

#class Test(SuperTest, SuperTest2):
    #pass

    #def test(self):
        #print "spoko"

    #def __init__(self):
        #super(Test, self).__init__()
        #SuperTest.__init__(self)
        #SuperTest2.__init__(self)
        

#Test()


#class Semantic(object):

    #OPERATION_FILE_FILTER = 1
    #OPERATION_TAG_FILTER
    #OPERATION_ATTRIBUTE_FILTER
    #OPERATION_SQL_FILTER = 3
    #OPERATION_DIRENTRY_FILTER = 4
    #OPERATION_DIRENTRY_GENERATOR

    #FEATURE_KEY_NODE_CAPABLE

    #def __init__(self):
        #self._flag_mask = 0
        #print dir(Semantic)

    #def is_set(flag):
        #pass
                   
    #def set(flag):
        #pass



#Semantic()
#class Semantic(object):

    #class AutoIncrementer:
        #@classmethod
        #def next(cls):
            #if not hasattr(cls, 'counter'):
                #cls.counter = 1
            #else:
                #cls.counter <<= 1
            #return cls.counter
                

    #OPERATION_FILE_FILTER        = AutoIncrementer.next()
    #OPERATION_TAG_FILTER         = AutoIncrementer.next()
    #OPERATION_ATTRIBUTE_FILTER   = AutoIncrementer.next()
    #OPERATION_SQL_FILTER         = AutoIncrementer.next()
    #OPERATION_DIRENTRY_FILTER    = AutoIncrementer.next()
    #OPERATION_DIRENTRY_GENERATOR = AutoIncrementer.next()

    #FEATURE_KEY_NODE_CAPABLE     = AutoIncrementer.next()

    #def __init__(self, mask = 0):
        #self._semantic_mask = mask
        #print dir(self)
    
    #def is_set(flag):
        #pass

    #def set(flag):
        #pass

#Semantic()
#print Semantic.OPERATION_FILE_FILTER
#print Semantic.OPERATION_TAG_FILTER

#class TestAbstract:
    #def filter(self):
        #self.filter_tags()

    #def filter_tags():
        #pass

#class Test(TestAbstract):
    #def filter_tags(self):
        #print 'filter_tags()'

#Test().filter()
#TestAbstract().filter()

class Test(object):
    def __init__(self, context, file_name):
        self.context = context
        self.file_name = file_name

    def __repr__(self):
        return str(self.context) + " " + str(self.file_name)

class SubTest(Test):
    def __init__(self, *args, **kw):
        super(SubTest, self).__init__(*args, **kw)


print SubTest('raz', 'dwa')

