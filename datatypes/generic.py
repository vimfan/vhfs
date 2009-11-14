import datetime
import parser as p

class Type:
    type_map = {}
    
    @staticmethod
    def cast(val):
        raise Exception, "Override cast() method"

class IntType(Type):
    @staticmethod
    def cast(node):
        try:
            val = int(node.value)
        except:
            raise Exception, "Cannot cast from %s to int", value
        return val

class StringType(Type):
    @staticmethod
    def cast(node):
        try:
            val = node.value
        except Exception, e:
            raise Exception, "Cannot cast from %s to string : %s" % (value, e)
        return val

class RealType(Type):
    @staticmethod
    def cast(node):
        try:
            val = float(node.value)
        except:
            raise Exception, "Cannot cast from %s to float", value
        return val
class DateType(Type):
    @staticmethod
    def cast(value):
        a = map(lambda x: int(x), value.split('-'))
        value = datetime.date(a[0], a[1], a[2])
        return value

class TimeType(Type):
    @staticmethod
    def cast(value):
        a = map(lambda x: int(x), value.split(':'))
        while len(a) < 3:
            a.append(0)
        value = datetime.time(a[0], a[1], a[2])
        return value

class TagType(Type):
    @staticmethod
    def cast(node):
        return p.TagNode(name = node.value, func_node = node.func_node)

class AttrType(Type):
    @staticmethod
    def cast(node):
        return p.AttrNode(name = node.name, func_node = node.func_node)

#class DateTimeType:
    #@staticmethod
    #def cast(value):
        #try:
            #a = value.split('@')
            #time_i = 0
            #date = []
            #if len(a) == 2:
                #date = map(lambda x: int(x), a[0].split('-'))
                #time_i = 1
            #elif len(a) == 1:
                #d = datetime.date.today()
                #date.append(d.year)
                #date.append(d.month)
                #date.append(d.day)
                #time_i = 0
            #time = map(lambda x: int(x), a[time_i].split(':'))
            #while len(time) < 3:
                #time.append(0)
            #return datetime.datetime(date[0], date[1], date[2], time[0], time[1], time[2])
        #except ValueError:
            #print "Bad DateTime format of %s", value


