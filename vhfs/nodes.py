import re
import vhfs_exceptions as exc
import parser

class NodeList(list):

    def __init__(self, l = [], parent = None):
        self.parent = parent
        for item in l:
            self.append(item)

    def __str__(self):
        prepare = [str(i) for i in self]
        return str(prepare)

    def __prepare_value(self, value):
        if (not isinstance(value, Node) and value <> None):
            value = ValueNode(value)
        value.parent = self.parent
        return value

    def __setitem__(self, i, value):
        return super(NodeList, self).__setitem__(i, self.__prepare_value(value))

    def __setslice__(self, i, j, y):
        prepared = NodeList(y)
        return super(NodeList, self).__setslice__(i, j, prepared)
        

    def __iadd__(self, y):
        prepared = NodeList(y)
        return super(NodeList, self).__iadd__(i, j, prepared)

    def __add__(self, y):
        out = []
        out.extend(self)
        out.extend(y)
        return NodeList(out)

    def append(self, value):
        return super(NodeList, self).append(self.__prepare_value(value))

    def extend(self, y):
        prepared = NodeList(y)
        return super(NodeList, self).extend(prepared)

    def insert(self, i, item):
        return super(NodeList, self).insert(i, self.__prepare_value(item))

class Node(object):
    '''
        Abstract class for all nodes used by parser.
    '''
        
    PRINT_ID = False

    def __init__(self, name, func_node = None, parent = None):
        # NOTE: self.__setattr__() is overriden
        self.parent = parent
        self.name = name
        self.func_node = func_node

    def _repr_injection(self):
        '''
            This method must be override by subclasses which needs non-standard
            string representations.

            @return: String which will be injected into string representation
                     of an instance
            @rtype: str
        '''
        return '%s%s' % (' ' + str(self.name), [' ' + str(self.func_node), ''][self.func_node is None])

    def __str__(self):
        injection = self._repr_injection()
        return "<# %s%s%s%s #>" % (self.__class__.__name__, \
            ['', '(id:' + `id(self)` + ')'][Node.PRINT_ID], \
            ['', ', parent id: ' + `id(self.parent)`][Node.PRINT_ID \
                and self.parent != None], injection)

    def __setattr__(self, item, val):
        if (not isinstance(val, Node) and val <> None):
            val = ValueNode(val)
        super(Node, self).__setattr__(item, val)
        val.parent = self

    def children(self):
        '''
            Returns all children nodes of this node.

            @return: Children nodes
            @rtype: list
        '''
        return [self.name, self.func_node]

    #def has_descendants_of_type(self, type):
        #'''
            #Check whether node has descendants of given type.

            #@param type: Type we are looking for
            #@type type: Subclass of Node
            #@return: True or False
            #@rtype: bool
        #'''
        #return len(filter(lambda x: isinstance(x, type) 
                    #or (hasattr(x, 'has_descendants_of_type') 
                    #and x.has_descendants_of_type(type)), self.children())) > 0

    def descendants_of_type(self, type):
        '''
            Returns all descendants of this node with given type.

            @param type: Type of descendants nodes.
            @type type: Node subclassess
            @return: List of nodes of given type
            @rtype: list
        '''
        if self.children() < 1:
            return []

        descendants = []
        queue = [self.children()[0]]
        while len(queue):
            n = queue.pop(0)
            if isinstance(n, type) and n <> self:
                descendants.append(n)
            queue.extend(n.children()) 
        return ancestors

    def replace_children_node(self, old, new):
        '''
            Replace a children node with another node.

            @param old: Node to replace
            @type old: Node
            @param new: Node to 
        '''
        new.parent = self
        if self.name == old:
            self.name = new
        elif self.func_node == old:
            self.func_node = new
        else:
            raise AttributeError()

    def remove_node(self, node):
        '''
            Removes given node from children.

            @param node: Node to remove
            @type node: Subclass of Node
        '''
        if self.func_node == node:
            self.func_node = None
        else:
            raise AttributeError()

    def operation_namespace():
        match = re.search('(.*)Node$', self.__class__.__name__)
        try:
            return match.groups[0]
        except:
            raise Exception, "Classes extending Node must have Node prefix in its names"
        
class PathNode(Node):

    def __init__(self, path = None, _name = 'Path', **kw):
        '''
        @param path: Path
        @type path: C{list} or C{str} or C{Node} or C{Path}
        '''
        super(PathNode, self).__init__(name = _name, **kw)
        self._nodes = NodeList(parent = self)
        if isinstance(path, list):
            self._nodes = filter(lambda item: isinstance(item, Node), path)
        elif isinstance(path, str):
            try:
                self._nodes = NodeList(self._parse(path), parent = self)
                self.__init__(self._nodes)
            except Exception, e:
                import sys
                import traceback
                print "Exception: %s\n%s \n%s" % (e, sys.exc_info(), \
                            traceback.extract_tb(sys.exc_traceback)) 
                self._nodes = NodeList(parent = self)
        elif isinstance(path, PathNode):
            self._nodes = path._nodes
        elif isinstance(path, Node):
            self._nodes.append(path)
        self._nodes = filter(lambda e: e <> None, self._nodes)

    def __setattr__(self, item, value):
        if item in ['_nodes']:
            return object.__setattr__(self, item, value)
        super(PathNode, self).__setattr__(item, value)

    def _parse(self, path):
        '''
        Parse path with syntax error toleration on the last node.
        
        @param path: String in format /foo/bar/dir/file
        @type path: str

        @return: Path
        @rtype: PathNode
        '''

        out = PathNode()

        try:
            out = parser.yacc.parse(path)
        except exc.VHFSException, e:
            path_parts = path.split('/')
            path_parts = filter(lambda x: x <> '', path_parts)
            path_parts = map(lambda x: '/' + x, path_parts)
            counter = len(path_parts)
            for i in xrange(counter):
                try:
                    path_part = self._parse(path_parts[i])
                    out += path_part
                except Exception, e:
                    out += PathNode(UnknownNode(name = path_parts[i][1:]))
        return out

    def _repr_injection(self):
        return ' %s ' % "/".join([str(x) for x in self._nodes])

    def __add__(self, path2):
        new_path = []
        new_path.extend(self._nodes)
        new_path.extend(path2._nodes)
        return PathNode(new_path)
 
    def __getitem__(self, i):
        return self._nodes[i]

    def __len__(self):
        return len(self._nodes)

    def __reversed__(self):
        return self._nodes.__reversed__()

    def key_node(self):
        '''
        Method returns the most crucial node which determines semantic of many
        actions. It's always last node which has one of semantics:
        FILE_SQL_FILTER or DIRENTRY_GENERATOR

        @return: The most crucial key node.
        @rtype: Node
        '''
        for child in reversed(self.children()):
            func_node = child.func_node
            if operations.Registry.semantic(func_node.operation_signature) in [operations.Semantic.FILE_SQL_FILTER, operations.Semantic.DIRENTRY_GENERATOR]:
                return child
            
    def children(self):
        '''
            Returns children of path node.

            @return: children nodes
            @rtype: list
        '''
        return self._nodes

    def replace_children_node(self, old, new):
        '''
            Replace old node with new node.

            @param old: Node to remove
            @type old: Node
            @param new: Node to insert instead of the old one
            @type new: Node

        '''
        i = self._nodes.index(old)
        self._nodes[i] = new 
       
    def remove_node(self, node):
        '''
            Remove node from a path.

            @param node: Node to remove
            @type node: Node
        '''
        i = self._nodes.index(node)
        del self._nodes[i]

    def insert_node(self, node, index = None):
        '''
            Insert node as children of a path.

            @param index: Index of element before node will be inserted.
            @type index: int

            @param node: Node
            @type node: Node
        '''
        if position is None:
            self._nodes.append(node)
        else:
            self._nodes.insert(index, node)

class FuncNode(Node):

    def __init__(self, name, args = [], public = True, instance_method = True, **kw):
        super(FuncNode, self).__init__(name, **kw)
        self._args = NodeList(args, parent = self)

        # flag indicates whether operation is public or private
        self.public = public

        # flag indicates whether operation is associated with particular instance
        # of some class (tag, attribute etc.)
        self.instance_method = instance_method

    def _set_public(self, value):
        object.__setattr__(self, '_public', bool(value))

    def _set_private(self, value):
        object.__setattr__(self, '_public', not bool(value))

    def _set_class_method(self, value):
        object.__setattr__(self, '_class', bool(value))

    def _set_instance_method(self, value):
        object.__setattr__(self, '_class', not bool(value))
        
    args = property(lambda self: self._args)
    public = property(lambda self: self._public, _set_public)
    private = property(lambda self: not self._public, _set_private)
    class_method = property(lambda self: self._class, _set_class_method)
    instance_method = property(lambda self: not self._class, _set_instance_method)

    def __setattr__(self, item, value):
        if item in ['_args', 'args']:
            if not isinstance(value, NodeList):
                value = NodeList(value, parent = self)
            return object.__setattr__(self, item, value)
        super(FuncNode, self).__setattr__(item, value)

    def _repr_injection(self):
        return (' ' + (['private', 'public'][int(self.is_public)]) 
                    + (['.', '::'][int(self.is_class_method)]) + str(self.name) 
                    + '(' 
                    + [','.join([str(arg) for arg in self.args]), ''][len(self.args) == 0] 
                    + ')')

    def children(self):
        l = super(FuncNode, self).children()
        l.extend(self.args)
        return filter(lambda x: x != None, l)

    def replace_children_node(self, old, new_node):
        i = self.args.index(old)
        self.args[i] = new_node

    def remove_node(self, node):
        i = self.args.index(node)
        del self.args[i]

    def operation_signature(self):
        '''
        Returns signature like: Tag.Public.Class.children

        @rtype: str
        '''
        parent = func_node.parent()
        parent_namespace = parent.operation_namespace()
        operation_parts = [parent_namespace]
        operation_parts.append('Public' if func_node.public else 'Private')
        if not func_node.instance_method:
            operation_parts.append('Class')
        operation_parts.append(func_node.name.value)
        return '.'.join(operation_parts)

class FileNode(Node):
    pass

class AttributeNode(Node):
    pass

class TagNode(Node):
    pass

class AmbigousNode(Node):
    pass

class NamespaceNode(Node):
    pass

class TypeCastNode(Node):
    def __init__(self, value = None, type = None, **kw):
        super(TypeCastNode, self).__init__(name = value, **kw)
        self.type  = type
        self.value = value

    def children(self):
        l = [super(TypeCastNode, self).children()]
        l.extend([self.type, self.value])
        return l

    def _repr_injection(self):
        return ' {%s:%s}' %  (
            str(self.type) + ['', str(self.func_node)][self.func_node <> None], 
            str(self.value)
        )

class UnknownNode(Node):
    pass

class ValueNode(Node):
    '''
        Class wrapper for values (instances of supported datatypes):
    '''

    def __init__(self, value):
        self._value = value

    def __str__(self):
        #return '%s:%s' % (self.value.__class__.__name__, str(self.value))
        return '%s' % str(self.value)

    def __setattr__(self, item, val):
        return object.__setattr__(self, item, val)

    value = property(lambda self: self._value)
    
    def children(self):
        return []
