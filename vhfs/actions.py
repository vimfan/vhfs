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
            return self._properties[item]
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

        @param path: Path to resolve
        @type path: PathNode
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

    class OperationResolver:
        '''
        Helper class used to store replaces for function nodes in two context:
        1. Normal (when node of a path isn't key node
        2. Key node (when node of a path is key node
        '''
        def __init__(self, normal, key_node = None):
            self._normal = normal
            self._key_node = normal if key_node is None else key_node

        normal = property(lambda self: copy.deepcopy(self._normal))
        key_node = property(lambda self: copy.deepcopy(self._key_node))

    def resolve_operation_defaults(self, path, defaults = None, empties = None):
        '''
        Resolve all FuncNode's with name member set to: '' (empty string)
        or TagNodes with empty FuncNode child.

        @param path
        @type PathNode

        @param defaults
        @type defaults list 

        @param empties 
        @type empties list

        Nodes like:  
            - C{<AttributeNode <FuncNode ()>>} 
              sets to: C{<AttributeNode <FuncNode default()>>}
            - C{<TagNode <FuncNode ()>>}
              sets to: C{<TagNode <FuncNode children()>>}
            - C{<TagNode>} 
              sets to: C{<TagNode <FuncNode has()>>}
        '''

        defaults_skeleton = {
            AttributeNode : OperationResolver(
                normal   = FuncNode('ignore', public = False, instance_method = False), 
                key_node = FuncNode('values', public = True,  instance_method = True)
            ),

            FileNode : OperationResolver(
                normal   = FuncNode('ignore', public = False, instance_method = False),
                key_node = FuncNode('meta',   public = False, instance_method = True)
            ),

            NamespaceNode : OperationResolver(
                normal   = FuncNode('ignore', public = False, instance_method = False),
                key_node = FuncNode('dir',    public = False, instance_method = False)
            ),

            TagNode : OperationResolver( 
                normal   = FuncNode('has',      public = False, instance_method = True),
                key_node = FuncNode('children', public = False, instance_method = True)
            )
        }

        empties_skeleton = {
            AttributeNode : OperationResolver(
                normal = FuncNode('ignore', public = False, instance_method = False)
                ),
            FileNode      : OperationResolver(
                normal = FuncNode('ignore', public = False, instance_method = False)
                ),
            NamespaceNode : OperationResolver(
                normal = Funcnode('ignore', public = False, instance_method = False),
                ),
            TagNode       : OperationResolver(
                normal = FuncNode('has', public = False, instance_method = True)
                )
        }

        if not defaults is None:
            for key in defaults.iter_keys():
                defaults_skeleton[key] = defaults[key]
        defaults = defaults_skeleton
            
        if not empties is None:
            for key in empties.iter_keys(): 
                empties_skeleton[key] = empties[key]
        empties = empties_skeleton

        key_node = path.key_node()

        for node in path.children():

            curr_class = node.__class__
            op_resolver = None

            if node.func_node is None:
                op_resolver = empties[curr_class]
            elif node.func_node.name.value == parser.UNSPECIFIED_SYM:
                op_resolver = defaults[curr_class]

            if not op_resolver is None:
                if not node is key_node:
                    node.func_node = op_resolver.normal 
                else:
                    node.func_node = op_resolver.key_node

    def sort_nodes(self, path, order = None):
        '''
        Performs sorting of C{path} respectively to the C{order}. Order is list which is permutation of flags defined in class Semantic.
        i.e. Semantic.FILE_SQL_FILTER, Semantic.SQL_FILTER etc.

        @param path: Path to perform sorting.
        @type path: PathNode

        @param order: Order given by list.
        @type order: list
        '''

        order_skeleton = [
            Semantic.FILE_SQL_FILTER,
            Semantic.SQL_FILTER,
            Semantic.DIRENTRY_GENERATOR,
            Semantic.DIRENTRY_FILTER,
            Semantic.REDUCIBLE_FILTER
        ]

        if order is None:
            order = order_skeleton

        def metric(semantic):
            '''
            @param semantic: Semantic
            @type semantic: Semantic

            @param order: List defining order. 
            @type order: list 
            '''
            for i in xrange(len(order)):
                if semantic.is_set(order[i]):
                    return i
            raise VHFSException("Semantic is unuseful %s" % semantic)

        def cmp(a, b):
            '''
            Function used to comparison.
            '''
            a_semantic = operation.Registry.semantic( a.func_node.operation_signature() ) 
            b_semantic = operation.Registry.semantic( b.func_node.operation_signature() ) 
            return metric(a_semantic) - metric(b_semantic)

        path.children.sort(cmp)
        
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

    def resolve_operation_defaults(self, path):
        super(ReaddirAction, self).resolve_operation_defaults(path)

    def remove_nodes(self, path):

        key_node = path.key_node()
        key_node_semantic = operations.Registry.semantic( key_node.func_node.operation_signature )

        def remove_nodes_without_semantic(children_nodes, semantic):
            '''
            Remove all nodes with semantic given by C{semantic_a}, but leaves
            those which has also C{semantic_b}. Condition is tested by is_set()
            method of semantic class.
            '''
            for node in children_nodes:
                semantic = operations.Registry.semantic( node.func_node.operation_signature )
                if not semantic.is_set(semantic_b):
                    node.parent().remove_children(node)

        if key_node_semantic.is_set(Semantic.DIRENTRY_GENERATOR):
            # remove all FILE_SQL_FILTER
            remove_nodes_without_semantic(Semantic.DIRENTRY_FILTER | Semantic.REDUCIBLE_FILTER)
            

        
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

        self.resolve_operation_names(c.path) 
        self.remove_nodes(c.path)

        # reduce nodes -> /@Func.limit:10/@Func.limit:200 => /@Func.limit:200

        # sort nodes
        self.sort_nodes(c.path)

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

