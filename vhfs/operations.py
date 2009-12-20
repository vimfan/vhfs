import models as m
import sys
import re

from sets import Set

import namespaces

class Semantic(object):

	def __init__(self, context):
		self.context = context


class Feature(Semantic):
    
	def __init__(self, *args, **kw):
		super(Feature, self).__init__(*args, **kw)

    def execute():
        pass


class Operation(Semantic):
	
	def __init__(self, *args, **kw):
		super(Operation, self).__init__(*args, **kw)

	def execute():
		pass


class KeyNodeCapable(Feature):
    pass
    #def nodes_to_remove():
        #pass


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

	def generate():
		pass

class DirentryGenerator(Generator):

	def generate(self):
		self.generate_direntries()


class Creator(Operation):

    def execute(self):
        self.create(self)
    
    def create():
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
    
    def execute(self):
        self.destroy()

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


class OperationsManager:

    def __init__(self):
        self.module = 'namespaces'
        self._namespace_names = []
        self._operations = {}
        for name in dir(test):
            obj = eval('%(module)s.%(name)s' 
                  % {'namespace' : self.module,'name' : name})
            if (obj.__class__ == test.Namespace.__class__ 
                and issubclass(o, test.Namespace) 
                and not obj is test.Namespace):
                namespace_name = obj.__name__
                self.namespace_names.append(namespace_name)
                for scope in ['Public', 'Private']:
                    scope_subclass_signature = '.'.join([namespace_name, scope])
                    try:
                        # e.g. 'Tag.Public'
                        scope_subclass = eval(scope_subclass_signature)
                        for semantic in dir(scope_subclass):
                            # e.g. 'Attribute.Public.Eq'
                            semantic_signature = '.'.join([scope_subclass, semantic])
                            self._operations[semantic_signature] = eval(semantic_signature)
                    except:
                        pass
                        
                        

    def _get_signature(self, namespace, operation_name, is_public = True, is_instance = True):
        '''
        Returns signature, e.g. for input:
            namespace = 'Tag'
            operation_name = 'Has'
            is_public = True
            is_instance = True

            self._get_signature(...) => 'Tag.Public.Has'

        @return: Signature
        @rtype: str
        '''
        assert len(namespace) > 0
        assert len(operation_name) > 0
        # Please note capitalization of the operation name(!)
        operation_name = operation_name.capitalize() 
        operation_name_parts = [namespace, 'Public' if is_public else 'Private']
        if not is_instance:
            operation_name_parts.append('Class')
        operation_name_parts.append(operation_name)
        return '.'.join(operation_name_parts)


    def get_operation(self, namespace, operation_name, is_public = True, is_instance = True):
        '''
        Returns operation object to execute.
        '''
        signature = self._get_signature(namespace, operation_name, is_public, is_instance)
        return self._operations[signature]()


    def is_operation_in_namespace(self, namespace, operation_name, is_public = True, is_instance = True):
        '''
        Checks whether operation with given C{name} is operation supported by
        given C{namespace}. Default search for public and instance operations.
            
        @param namespace Name of the namespace
        @type namespace str
 
        @param operation_name Name of the operation
        @type operation_name str
 
        @param is_public True if method public, false if private.
        @type bool 
 
        @param is_instance True if method is an instance method of some
                           instance (Tag.Has, Attribute.Eq etc.), False if it's
                           class method (e.g. Func.limit)
        @type bool 
 
        @return True if operation is provided by namespace, false if not.
        @rtype bool
        '''
        signature = self._get_signature(namespace, operation_name, is_public, is_instance)
        return self._operations.has_key(signature)
        
    def get_namespaces_by_operation(self, name, is_public = True, is_instance = True):
        '''
        Gets all namespaces which implements operation given by name and satisfies
        conditions is_public and is_instance.
        '''
        namespaces = []
        for namespace in self._namespace_names:
            if is_operation_from_namespace(namespace, name, is_public, is_instance):
                namespaces.append(namespace)
        return namespaces


    def get_namespace_names(self):
        '''
        Returns names of all available namespaces.
        '''
        return copy.deepcopy(self._namespace_names)


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
          
