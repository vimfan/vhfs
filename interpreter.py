from datatypes.generic import *
import models as m
import copy
import meta_data_manager
import parser
import re
import logging
import errno

from nodes import *

class Context(object):
    '''
    Context class definition.

    Operation member must always be set to name of the operation by which
    interpreter is invoked.

    Allowed fields are now:
        1. FS Api - specyfic
            - operation, path, path2, times, flags, mode, rdev, offset
        2. Interpreter specyfic
            - steps_num, curr_step, next_step, registry

    '''
    def __init__(self):
        self.__properties = {}
        self.__permitted_keys = [
            # fuse implementation dependable fields
            'operation', 'path', 'path2', 'times', 
            'flags',     'mode', 'rdev',  'offset',
            # interpreter fields
            'steps_num', 'curr_step', 'next_step'
            # registry storage for use by interpreters
            'registry'
        ]
        self.__properties['steps_num'] = 1
        self.__properties['curr_step'] = 0
        self.__initialized = True

    def __str__(self):
        return '<# Context %s #>' % `self.__properties`

    def __getattr__(self, item):
        try:
            return self.__properties[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        if not self.__dict__.has_key('_Context__initialized'):
            return object.__setattr__(self, item, value)
        elif item in self.__permitted_keys:
            self.__properties[item] = value
        else:
            raise AttributeError(item)

class IInterpreter(object):
    def eval():
        '''
            Performs evaluation of an object.

            This method must be overloaded by classes implementing this interface.
        '''
        raise VHFSOverloadException()

class Interpreter(IInterpreter):
    '''Entry class for interpreting context.'''

    def __init__(self, context):
        self.__context = context

    def eval(self):
        '''
            Performs parsing for at least one path (self.__context.path), and
            if is second path (set self.__context.path. Invokes appropriate
            interpreter at least one time.
        '''
        # PathNodeInterpreter implementation decides how many steps it needs,
        # so self.__context.steps_num may be changed by ivoked interpreter
        while self.__context.curr_step < self.__context.steps_num:
            class_name = self.__context.operation.capitalize() + 'Interpreter'
            interpreter = eval('%s(self.__context)' % class_name)
            interpreter.eval()
            self.__context.curr_step += 1

        return self.__context.out

    
class AbstractInterpreter(IInterpreter):

    def __init__(self, context):
        self.__context = context

class ReaddirInterpreter(AbstractInterpreter):
    '''
        Interpreter for readdir FS api operation. One condition is obligatory:
            1. Context must have B{path} member correctly initialized, path must be
            grammaticaly correct. 
    '''
    def eval(self):
        '''
        Interprets path.

        @return: List of direntries (files or directories). For every item in
        the list ivocation for getattr(full_path_to_item) must return
        appropriate instance of Fuse.Stat type.
        '''
        path = PathNode(self.__context.path)
        if len(filter()):
            pass
        # filter nodes
        # reduce nodes
        # sort nodes
        # add InterpreterHelperNode instance
        # for every node perform eval()
        # return context.out


class AccessInterpreter(AbstractInterpreter):
    def eval(self):
        pass

class GetattrInterpreter(AbstractInterpreter):
    def eval(self):
        pass

class MkdirInterpreter(AbstractInterpreter):
    def eval(self):
        pass

class RmdirInterpreter(AbstractInterpreter):
    def eval(self):
        pass

class RenameInterpreter(AbstractInterpreter):
    def eval(self):
        pass

class SymlinkInterpreter(AbstractInterpreter):
    def eval(self):
        pass

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
        interpreter_class_name = self.node.__class__.__name__ + 'Interpreter'
        interpreter = eval('NodeInterpreter.%s(self.node, self.context)' %
                            interpreter_class_name)
        interpreter.eval()

    class PathNodeInterpreter(AbstractNodeInterpreter):
        
        def __init__(self, *arg, **kw):
            super(PathNodeInterpreter, self).__init__(*arg, **kw)
            #self._mdmgr = meta_data_manager.MetaDataManager.getInstance()

        def eval(self):
            prefix = self.__class__.__name__
            for child in self.children():
                interpreter_class_name = child.__class__.__name__ + 'Interpreter'
                interpreter = eval('%s(self.context, child)' % interpreter_class_name)
                interpreter.eval()

    class NamespaceNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('NamespaceNodeInterpreter')

    class TagNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('TagNodeInterpreter')

    class AttributeNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('TagNodeInterpreter')

    class FileNodeInterpreter(AbstractNodeInterpreter):
        def eval(self):
            logging.debug('TagNodeInterpreter')

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
                if self.__mdmgr.is_only(self.node.name.value, cls_name):
                    new_node_type = eval(cls_name + 'Node')

                if new_node_type == None:

                    if node.func_node == None:
                        new_node_type = TagNode

                    elif node.func_node.name != UNSPECIFIED_SYM:
                        operation_name = node.func_node.name 
                        for cls in possible_classes:
                            namespace = cls
                            if cls == 'Namespace':
                                op_name   = m.NAMESPACE_METHOD_PREFIX + operation_name
                                namespace = node.name
                            else:
                                op_name = operation_name
                            if self._mdmgr.is_operation_of(op_name, namespace):
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

    class ValueNodeIntereter(AbstractNodeInterpreter):
        def eval(self, node):
            pass
