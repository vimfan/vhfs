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

    def eval(self):
        '''
        Performs parsing for at least one path (self.__context.path), and if
        second path exists (set self.__context.path2) it invokes appropriate
        interpreter at least one time.
        '''

        # PathNodeInterpreter implementation decides how many steps it needs,
        # so self.__context.steps_num may be changed by ivoked interpreter
        while self._context.curr_step < self._context.steps_num:
            interpreter = Interpreter(self._context)
            self._context.curr_step += 1

        return self.__context.out

    def build_interpreter(self):
        class_name = self.__context.operation.capitalize() + 'Interpreter'
        interpreter = eval('%s(self.__context)' % class_name)
        interpreter.eval()

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
        logging.debug(self.__class__.__name__)


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

    def eval(self):
        interpreter_impl_class_name = self.node.__class__.__name__ + 'Interpreter'
        interpreter_impl = eval('NodeInterpreter.%s(self.node, self.context)' %
                            interpreter_impl_class_name)
        interpreter_impl.eval()

    class PathNodeInterpreter(AbstractNodeInterpreter):
        
        def __init__(self, *arg, **kw):
            super(PathNodeInterpreter, self).__init__(*arg, **kw)
            #self._mdmgr = meta_data_manager.MetaDataManager.getInstance()

        def eval(self):
            self.eval_children()

    class NamespaceNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('NamespaceNodeInterpreter')
            self.eval_children()

    class TagNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('TagNodeInterpreter')
            self.eval_children()
            operations.eval(Tag, self.node.name.value, 
                self.node.func_node.name.value, *self.node.func_node.args)


    class AttributeNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('AttributeNodeInterpreter')
            self.eval_children()
            operations.eval(Attribute, self.node.name.value, 
                        self.node.func_node.name, *self.node.func_node.args)

    class FileNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('TagNodeInterpreter')
            self.eval_children()

    class AmbigousNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            '''
            Resolves type of the given node by checking its operation and
            metadata information stored in database backend. In its parent node
            replace reference to the given node by new created node.

            @param node: Node to resolve ambiguity
            @type node: AmbigousNode
            '''
            new_node_type = None
            possible_classes = ['Attribute', 'Tag', 'Namespace']
            for cls_name in possible_classes:
                if self._metadata_mgr.is_only(self.node.name.value, cls_name):
                    new_node_type = eval(cls_name + 'Node')

                if new_node_type is None:

                    if node.func_node is None:
                        new_node_type = TagNode

                    elif node.func_node.name != UNSPECIFIED_SYM:
                        operation_name = node.func_node.name 
                        for cls in possible_classes:
                            namespace = cls
                            if cls == 'Namespace':
                                op_name = m.NAMESPACE_METHOD_PREFIX + operation_name
                                namespace = node.name
                            else:
                                op_name = operation_name
                            if self._metadata_mgr.is_operation_of(op_name, namespace):
                                new_node_type = eval(cls + 'Node')
                                
                if new_node_type == AttributeNode:
                    new_node = AttributeNode(name = node.name, 
                                             func_node = node.func_node, 
                                             parent = parent)
                elif new_node_type == TagNode:
                    new_node  = TagNode(name = node.name, 
                                        func_node = func_node, 
                                        parent = parent)
                elif new_node_type == NamespaceNode:
                    new_node  = NamespaceNode(name = node.name, 
                                              func_node = node.func_node, 
                                              parent = parent)
                else:
                    new_node = None
                if new_node != None:
                    parent.replace_subnode(node, new_node)
                else:
                    raise VHFSException(msg='Cannot resolve ambigous Node %s' 
                                             % node, err_code = errno.EBADMSG)

    class TypeCastNodeInterpreter(AbstractNodeInterpreter):
        '''Class for interpreting nodes of type TypeCastNode'''

        def eval(self, node):
            '''
            Resolves type of the given node. Replace reference to the given node
            by new resolved node in his parent node.

            @param node: Node to resolve using hint
            @type node: TypeCastNode
            '''
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
            parent.replace_subnode(node, new_node)

    class ValueNodeInterpreter(AbstractNodeInterpreter):
        def eval(self, node):
            '''
            No evaluation is needed for instances of ValueNode

            @param node: Node to evaluate
            '''
            pass
