import models as m
import sys
import re

from sets import Set

class Semantic(object):

	def __init__(self, context):
		self.context = context


class Feature(Semantic):
    
	def __init__(self, *args, **kw):
		super(Feature, self).__init__(*args, **kw)


class Operation(Semantic):
	
	def __init__(self, *args, **kw):
		super(Operation, self).__init__(*args, **kw)

	def execute():
		pass


class KeyNodeCapable(Feature):

    def nodes_to_remove():
        pass


class Filter(Operation):

	def execute(self):	
		self.filter(self)

	def filter(self):
		pass


class FileFilter(Filter):

	def filter(self):
		self.filter_files()


class TagFilter(Filter):

	def filter(self):
		self.filter_tags()


class AttributeFilter(Filter):

	def filter(self):
		self.filter_attributes()


class SQLFilter(Filter):

	def filter(self):
		self.filter_by_sql()


class DirentryFilter(Filter):

	def filter(self):
		self.filter_direntries()


class Generator(Operation):

	def execute(self):
		self.generate(self)

	def generate(self):
		pass

class DirentryGenerator(Generator):

	def generate(self):
		self.generate_direntries()


class Creator(Operation):

    def execute(self):
        self.create(self)
    
    def create(self):
        pass

class AttributeCreator(Creator):

    def __init__(self, key, value, *args, **kw):
        super(Creator, self).__init__(*args, **kw)
        self.attr_key = key
        self.attr_value = value
        self.created_attribute = None

    def create(self):
        self.create_attribute()

    def create_attribute(self):
        self.created_attribute = m.Attribute(key=self.attr_key, value=self.attr_value)

class TagCreator(Creator):

    def __init__(self, name, *args, **kw):
        super(Creator, self).__init__(*args, **kw)
        self.tag_name = name
        self.created_tag = None
    
    def create(self):
        self.create_tag()

    def create_tag(self):
        self.created_tag = m.Tag(name=self.tag_name)

class FileCreator(Creator):

    def __init__(self, file_name, *args, **kw):
        super(Creator, self).__init__(*args, **kw)
        self.file_name = file_name
        self.created_file = None
    
    def create(self):
        self.create_file()

    def create_file(self):
        self.created_file = m.File(file_name=self.file_name)


class AssociationCreator(Creator):
    
    def create(self):
        self.create_association()


class Destroyer(Operation):
    
    def 

class AssociationDestroyer(Destroyer):
    
    def destroy(self):
        self.destroy_association()

class FileDestroyer(Destroyer):
    
    def destroy(self):
        self.destroy_file()

class TagDestroyer(Destroyer):
    
    def destroy(self):
        self.destroy_tag()


class AttributeDestroyer(Destroyer):
    
    def destroy(self):
        self.destroy_attribute()


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
