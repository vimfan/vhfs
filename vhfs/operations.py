import models as m
import sys
import re

from namespaces import *

class Semantic:

    FILE_SQL_FILTER = 0x0001 
    '''@cvar: When operation adds some filtering to query on File table'''
    SQL_FILTER = 0x0002
    '''@cvar: General SQL filtering operations like: limit, offset etc.'''
    DIRENTRY_GENERATOR = 0x0004
    '''@cvar: This kind of operations don't modify context.query'''
    DIRENTRY_FILTER = 0x0008
    '''@cvar: Filter which can be applied for C{context.out} rather in contradiction
       to SQL_FILTER which can be only applied to C{context.query}'''
    REDUCIBLE_FILTER = 0x0020
    '''@cvar: Some filters may be reducted to one filter, e.g 
       /@Func.limit:10/@Func.limit:20 => /@Func.limit:20'''

    def __init__(self, flags):
        possible_flags = ['FILE_SQL_FILTER', 'SQL_FILTER', 
                                 'DIRENTRY_GENERATOR', 'DIRENTRY_FILTER', 
                                 'REDUCIBLE_FILTER']
        for item in possible_flags: 
            eval('self.%(field_name)s = (Semantic.%(flag)s & flags) != 0 ' \
                % {'field_name' : item.lower(), 'flag' : item})

class Registry:

    _entries = []

    class Entry:
        pass

    class OperationEntry(Entry):

        def __init__(self, operation, semantic_flags):
            self.operation = operation
            self.semantic = Semantic(semantic_flags)

    @classmethod
    def append_operation(cls, operation, semantic):
        '''
        Add new entry to the registry.
        '''
        cls._entries.append(cls.OperationEntry(operation, semantic))

    @classmethod
    def semantic(cls, operation):
        '''
        Returns semantic of the operation given by E{operation}. 

        @return: Semantic indicator
        @rtype: Semantic
        '''
        for entry in cls._entries:
            if entry.operation == operation:
                return entry.semantic

def semantic(semantic_indicator):
    '''
    Generates decorator function for operations. Every decorator generated by
    its wraps method with staticmethod decorator.

    @param semantic_indicator: Parameter indicating semantic.
    @type semantic_indicator: Semanticfield
    '''
    decorator_name = 'semantic_' + str(semantic_indicator)
    exec('''
def %s(f):
    i = 1
    trace = []
    trace.insert(0, f.func_name)
    while True:
        level = sys._getframe(i).f_code.co_name
        if re.search("module", stair):
            break
        trace.insert(0, level)
        i += 1
    operation_name = ".".join(trace)
    Registry.append_entry(operation_name, %s)
    return staticmethod(f)
''' % (decorator_name, semantic_indicator))
    return eval(decorator_name)

class Namespace(object):
    def dir():
        '''
        Operation which lets user see all operations supported by
        the namespace.
        '''
        pass
          
