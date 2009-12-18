import copy
import re
import logging
import errno

import models as m
import meta_data_manager
import parser
import operations

from nodes import *
from datatypes.generic import *

import actions

class IInterpreter(object):
    def eval():
        '''
        Performs evaluation of an object.

        This method must be overloaded by classes implementing this interface.
        '''
        raise VHFSOverloadException()

class Interpreter(IInterpreter):
    '''
    Entry class for interpreting context.
    '''

    def __init__(self, context):
        self._context = context

    #def eval(self):
        #'''
        #Performs parsing for at least one path (self._context.path), and if
        #second path exists (set self._context.path2) it invokes appropriate
        #interpreter at least one time.
        #'''
        # PathNodeInterpreter implementation decides how many steps it needs,
        # so self._context.steps_num may be changed by ivoked interpreter
        #while self._context.curr_step < self._context.steps_num:
            #action = build_action()
            #action.perform()
            #self._context.curr_step += 1

        #return self._context.out

    #def build_action(self):
        #class_name = self._context.operation.capitalize() + 'Action'
        #action = eval('%s(self._context)' % class_name)
        #return action

class AbstractNodeInterpreter(IInterpreter):

    def __init__(self, context, node = None):
        '''
        Initializes instance with read-only members: node, context.

        @param context: Current context.
        @type context: Context

        @param node: Node to interpret.
        @type node: Node
        '''
        self._context = context
        self._node = node
        self._metadata_mgr = MetaDataManager.get_instance()

    def __str__(self):
        return '<# %s (%s) #>' % (self.__class__.__name__, str(self.node))

    def eval_children(self):
        for node in self.children():
            node_interpreter = NodeInterpreter(node)
            node_interpreter.eval()

    node = property(lambda self: self._node)
    '''
    @ivar: Read only field
    @type: C{Node}
    '''

    context = property(lambda self: self._context)
    '''
    @ivar: Read only field
    @type: C{Context}'''

class NodeInterpreter(AbstractNodeInterpreter):

    def __init__(self, *arg, **kw):
        super(NodeInterpreter, self).__init__(*arg, **kw)
        self.interneter_impl = None

    def eval(self):
        self.build_interpreter().eval()

    def build_interpreter(self):
        interpreter_impl_class_name = self.node.__class__.__name__ + 'Interpreter'
        return eval('NodeInterpreter.%s(self.node, self.context)' %
                    interpreter_impl_class_name)

    class PathNodeInterpreter(AbstractNodeInterpreter):
        
        def __init__(self, *arg, **kw):
            super(PathNodeInterpreter, self).__init__(*arg, **kw)
            self._mdmgr = meta_data_manager.MetaDataManager.getInstance()

        def eval(self):
            self.eval_children()

    class NamespaceNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            logging.debug('NamespaceNodeInterpreter.eval_children() : Start')
            self.eval_children()
            logging.debug('NamespaceNodeInterpreter.eval_children() : End')

    class TagNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            logging.debug('TagNodeInterpreter.eval_children() : Start')
            self.eval_children()
            logging.debug('TagNodeInterpreter.eval_children() : End')
            logging.debug('TagNodeInterpreter.eval() : Start')
            operations.eval(Tag, self.node.name.value, 
                self.node.func_node.name.value, *self.node.func_node.args)
            logging.debug('TagNodeInterpreter.eval() : End')


    class AttributeNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            logging.debug('AttributeNodeInterpreter.eval_children() : Start')
            self.eval_children()
            logging.debug('AttributeNodeInterpreter.eval_children() : End')
            logging.debug('AttributeNodeInterpreter.eval() : Start')
            operations.eval(Attribute, self.node.name.value, 
                            self.node.func_node.name, 
                           *self.node.func_node.args)
            logging.debug('AttributeNodeInterpreter.eval() : End')

    class FileNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            logging.debug('FileNodeInterpreter.eval_children() : Start')
            self.eval_children()
            logging.debug('FileNodeInterpreter.eval_children() : End')

    class FuncNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            logging.debug('FuncNodeInterpreter.eval_children() : Start')
            self.eval_children()
            logging.debug('FuncNodeInterpreter.eval_children() : End')
            

    class AmbigousNodeInterpreter(AbstractNodeInterpreter):

        def eval(self):
            '''
            Resolves type of the given node by checking
            1. metadata stored in database 
            2. its operation (specified by func_node which is subnode of given node) 

            After resolving it replaces reference to the given node by new created
            one in its parent.
            '''
            new_node_type = None
            node = self.node
            node_name = self.node.name.value
            operation_name = node.func_node.name.value 

            if self._metadata_mgr.is_namespace(node.name.value):
                namespace_name = node_name
                if operations.Registry.is_namespace_operation(namespace_name, 
                                                              operation_name, 
                                                              is_instance = False):
                    new_node_type = NamespaceNode
            else:
                if self._metadata_mgr.is_attribute(node_name):
                    new_node_type = AttributeNode
                if self._metadata_mgr.is_tag(node_name):
                    if new_node_type == None:
                        new_node_type = TagNode
                    else:
                        # if node_name may be the name of a tag or name of an attribute
                        # then it decides which to choose by the operation_name
                        new_node_type = None
                        if operations.is_namespace_operation('Attribute', operation_name):
                            new_node_type = AttributeNode
                        if operations.is_namespace_operation('Tag', operation_name):
                            if new_node_type == None:
                                new_node_type = TagNode
                            else:
                                new_node_type = None
            if new_node_type is AttributeNode:
                new_node = AttributeNode(name = node.name, 
                                         func_node = node.func_node, 
                                         parent = node.parent)
            elif new_node_type is TagNode:
                new_node  = TagNode(name = node.name, 
                                    func_node = func_node, 
                                    parent = node.parent)
            elif new_node_type is NamespaceNode:
                new_node  = NamespaceNode(name = node.name, 
                                          func_node = node.func_node, 
                                          parent = node.parent)
            else:
                new_node = None

            if new_node != None:
                parent.replace_children(node, new_node)
            else:
                raise VHFSException(msg='Cannot resolve ambigous Node %s' 
                                         % node, err_code = errno.EBADMSG)
            
    class TypeCastNodeInterpreter(AbstractNodeInterpreter):
        '''Class for interpreting nodes of type TypeCastNode'''

        def eval(self):
            '''
            Resolves type of the given node. Replace reference to the given node
            by new resolved node in his parent node.
            '''
            node = self.node
            parent = node.parent
            type = node.type  
            value = node
            type_class = type.capitalize() + 'Type'
            type_module = 'datatypes.' + type.lower() + '_type'
            try:
                exec 'new_node = %s.cast(%s)' % (type_class, 'value')
            except AttributeError, e:
                exec 'import %s' % type_module
                exec 'new_node = %s.cast("%s")' % (type_module + '.' + type_class, value)
            parent.replace_children(node, new_node)

    class ValueNodeInterpreter(AbstractNodeInterpreter):
        def eval(self, node):
            '''
            No evaluation is needed for instances of ValueNode

            @param node: Node to evaluate
            '''
            pass
