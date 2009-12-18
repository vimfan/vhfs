import models as m
import sys
import re

from sets import Set

class Semantic:

    FILE_SQL_FILTER = 0x0001 
    '''@cvar: When operation adds some filtering to query on files table'''

    TAG_SQL_FILTER = 0x0001 
    '''@cvar: When operation adds some filtering to query on files table'''

    ATTRIBUTE_SQL_FILTER = 0x0001 
    '''@cvar: When operation adds some filtering to query on files table'''

    SQL_FILTER = 0x0002
    '''@cvar: General SQL filtering operations like: limit, offset etc.'''

    DIRENTRY_GENERATOR = 0x0004
    '''@cvar: Oerations which don't modify context.query, returns list of
              direntries instead'''

    DIRENTRY_FILTER = 0x0008
    '''@cvar: Filter which can be applied for C{context.out} rather in
              contradiction to SQL_FILTER which can be only applied to
              C{context.query}'''

    REDUCIBLE_FILTER = 0x0020
    '''@cvar: Some filters may be reducted to one filter, e.g 
              /@Func.limit:10/@Func.limit:20 => /@Func.limit:20'''

    NONE_FILTER = 0x0040

    def __init__(self, flags):
        self._possible_flags = ['FILE_SQL_FILTER', 
                                'SQL_FILTER', 
                                'DIRENTRY_GENERATOR', 
                                'DIRENTRY_FILTER', 
                                'REDUCIBLE_FILTER']
        self._flags = flags
        
    flags = property(lambda self: self._flags)

    def __getattr__(self, item):
        uppercase_item = item.upper()
        if uppercase_item in self._possible_flags:
            return bool(eval('Semantic.%s' % uppercase_item) & self.flags)
        else:
            AttributeError(item)

    def is_set(self, mask):
        return bool(self.flags & mask)
        
    def __repr__(self):
        flags = []
        for flag in self._possible_flags:
            if eval('self.%(field_name)s' % {'field_name' : flag.lower() }):
                flags.append(flag)
        return "<# Semantic " + ' | '.join(flags) + " >"

class Registry:

    _entries = {}
    _namespaces = []

    class Entry:
        pass

    class OperationEntry(Entry):

        def __init__(self, operation, semantic_flags):
            '''
            @param operation: Operation name
            @type operation: str

            @param semantic_flags: Bitwise conjunction of flags from set: Semantic.*
            @type: int
            '''
            self.operation = operation
            self.semantic = Semantic(semantic_flags)

        def __repr__(self):
            return "%s semantic: %s" % (self.operation, self.semantic)

    @classmethod
    def append_operation(cls, operation, semantic):
        '''
        Add new entry to the registry.

        @param operation: String like Tag.Public.Class.dir, in general: {Namespace}.{Public|Private}[.Class].{operation}
        @type operation: str

        @param semantic: Semantic of given operation
        @type semantic: Semantic

        @return: None
        '''
        cls._entries[operation] = (cls.OperationEntry(operation, semantic))
        cls._namespaces.append(operation.split('.')[0])
        cls._namespaces = list(Set(cls._namespaces))

    @classmethod
    def semantic(cls, operation):
        '''
        Returns semantic of the operation given by E{operation}. 

        @param operation: Operation
        @type operation: instancemethod

        @return: Semantic indicator
        @rtype: Semantic
        '''
        for entry in cls._entries:
            if entry.operation == operation:
                return entry.semantic

    @classmethod
    def is_namespace_operation(cls, namespace, name, is_public = True, is_instance = True):
        '''
        Check whether operation with given C{name} is operation supported by
        given C{namespace}. Default search for public and instance operations.
            
        @param namespace Name of the namespace
        @type namespace str

        @param name Name of the operation
        @type name str

        @param is_public Flag points if method is public or private
        @type bool 

        @param is_instance Flag points if method is instance or class method (static)
        @type bool 

        @return True if operation is provided by namespace, false if not.
        @rtype bool
        '''
        operation_name = ("%(namespace)s.%(scope)s" 
            % {'namespace' : namespace, 'scope' : 'Public' if is_public else 'Private'})
        if not is_instance:
            operation_name += '.Class'
        operation_name += '.' + name
        return cls._entries.has_key(operation_name)

    @classmethod
    def get_namespaces_by_operation(cls, name, is_public = True, is_instance = True):
        namespaces = []
        for namespace in cls._namespaces:
            if cls.is_namespace_operation(namespace, name, is_public, is_instance):
                namespaces.append(namespace)
        return namespaces

    @classmethod
    def get_namespaces(cls):
        return cls._namespaces


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
        if re.search("module", level):
            break
        trace.insert(0, level)
        i += 1
    operation_name = ".".join(trace)
    Registry.append_operation(operation_name, %s)
    return staticmethod(f)
''' % (decorator_name, semantic_indicator))
    return eval(decorator_name)

class Namespace(object):

    @classmethod
    def dir():
        '''
        Operation which lets user see all operations supported by
        the namespace.
        '''
        pass

    @classmethod
    def ignore(cls):
        pass
          
from namespaces import *
