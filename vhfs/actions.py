import errno

import models as m
import meta_data_manager
import parser
import operations

from vhfs_exceptions import *
from nodes import *
from datatypes.generic import *

class Context(object):
    '''
    Context class definition.

    Operation member must always be set to the name of the operation by which
    interpreter is invoked.

    Allowed fields are now:
        1. FS Api - specific
            - operation, path, path2, times, flags, mode, rdev, offset
        2. Interpreter specyfic
            - steps_num, curr_step, next_step, registry

    '''
    def __init__(self):
        self._properties = {}
        self._permitted_keys = [
            # fuse implementation dependable fields
            'operation', 'path', 'path2', 'times', 
            'flags',     'mode', 'rdev',  'offset',
            # interpreter fields
            'steps_num', 'curr_step', 'next_step'
            # registry storage for use by interpreters
            'registry', 'query'
        ]
        self._properties['steps_num'] = 1
        self._properties['curr_step'] = 0
        self._initialized = True

    def __str__(self):
        return '<# Context %s #>' % `self._properties`

    def __getattr__(self, item):
        try:
            return self.__properties[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        if not self.__dict__.has_key('_initialized'):
            return object.__setattr__(self, item, value)
        elif item in self._permitted_keys:
            self._properties[item] = value
        else:
            raise AttributeError(item)

class IAction(object):
    def perform():
        pass

class IFilesystemAction(IAction):
    pass

class AbstractFilesystemAction(IFilesystemAction):

    def __init__(self, context):
        self._context = context

    context = property(lambda self: self._context)
    '''
    @ivar : Context member. Read-only.
    '''

    def resolve_ambigouity(self, path):
        '''
        Resolves ambigouity when it's possible.
        '''
        ambigous_nodes = path.descendants_of_type(AmbigousNode)
        for node in ambigous_nodes:
            NodeInterpreter(node, self._context).eval()

    def perform_type_casting(self, path):
        '''
        Performs type casting.

        @param path: Path on which nodes will be casted.
        @type path: PathNode
        '''
        type_cast_nodes = path.descendants_of_type(TypeCastNode)
        for node in type_cast_nodes:
            NodeInterpreter(node, self._context).eval()

    def resolve_operation_defaults(self, path):
        '''
        Resolve all FuncNode's with name member set to: '' (empty string)
        or TagNodes with empty FuncNode child.

        Nodes like:  
            - C{<AttributeNode <FuncNode ()>>} 
              sets to: C{<AttributeNode <FuncNode default()>>}
            - C{<TagNode <FuncNode ()>>} 
              sets to: C{<TagNode <FuncNode children()>>}
            - C{<TagNode>} 
              sets to: C{<TagNode <FuncNode has()>>}
        '''
        defaults = {
            AttributeNode : 'values',
            TagNode       : 'children',
            NamespaceNode : 'dir',
        }
        empties = {
            TagNode       : 'has',
            NamespaceNode : 'dir'
        }
        

    def resolve_operation_names(self, path, func):

        func_nodes = path.descendants_of_type(FuncNode)

        for node in func_nodes:
            name_parts = []
            name = node.name.value
            class_name = node.parent.__class__.__name__[0:-4]
            if class_name in ['AttributeNode', 'TagNode']:
                pass
            elif class_name == 'NamespaceNode':
                pass
            else:
                continue
            node.name.value = '.'.join(name_parts)
                

    def perform_reductions(self, path):
        '''
        Performs reductions of some reductable nodes.
        '''
        pass


class ReaddirAction(AbstractFilesystemAction):
    '''
        Action implementation for readdir FS api operation. One condition is obligatory:
            1. Context must have B{path} member correctly initialized. Path must be
            grammaticaly valid to perform read of directory. 
    '''

    def perform(self):
        '''
        Interprets path.

        @return: List of direntries (files or directories names as strings). For
        every item in the list ivocation for getattr(full_path_to_item) must return
        appropriate instance of Fuse.Stat type.
        '''
        context = self.context 
        context.path = PathNode(c.path)

        if filter(lambda x: isinstance(x, UnknownNode), path.children()):
            raise VHFSException(msg = 'Unkonown Node : %s' % str(UnkonownNode), 
                err_code = errno.ENOENT)

        self.perform_type_casting(context.path)
        self.resolve_ambigouity(context.path)

        # e.g. @tag => Tag.Private.has(tag.name)
        # @tagname. => Tag.Public.children(tagname), @Func. => Func.Public.Class.dir
        # self.resolve_operation_names(c.path) 

        # filter nodes

        # reduce nodes -> /@Func.limit:10/@Func.limit:200 => /@Func.limit:200

        # sort nodes

        interpreter = NodeInterpreter(context, context.path)
        interpreter.eval()

        return context.out

class AccessAction(AbstractFilesystemAction):
    def perform(self):
        pass

class GetattrAction(AbstractFilesystemAction):
    def perform(self):
        pass

class MkdirAction(AbstractFilesystemAction):
    def perform(self):
        pass

class RmdirAction(AbstractFilesystemAction):
    def perform(self):
        pass

class RenameAction(AbstractFilesystemAction):
    def perform(self):
        pass

class SymlinkAction(AbstractFilesystemAction):
    def perform(self):
        pass

