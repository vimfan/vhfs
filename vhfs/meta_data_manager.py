import singleton
import errno

import operations
import models

from parser import *
from interpreters import *

class MetaDataManager(singleton.Singleton):

    def __init__(self):
        self._tags       = None
        self._tag_names  = None
        self._attrs      = None
        self._attr_keys  = None
        self._namespaces = operations.Registry.get_namespaces()

        self.refresh_tags()
        self.refresh_attrs()

    @classmethod
    def get_instance(cls):
        '''
            Wrapper to be convention valid.

            @return: One and only MetaDataManager instance.
            @rtype: MetaDataManager
        '''
        return MetaDataManager.getInstance(cls)

    def get_tag(self, name):
        '''
            Returns tag instance which has given name.

            @param name: Name of a tag
            @type name: str

            @return: Tag instance with given name
            @rtype: Tag
        '''
        for tag in self._tags:
            if tag.name == name:
                return tag
        return None

    def add_tag(self, tag):
        '''
            Adds new tag to the index.

            @param tag: Tag instance to add.
            @type tag: Tag
        '''
        if not self.get_tag(tag.name):
            self._tags.append(tag)
            self._tag_names.append(tag.name)

    def del_tag(self, tag):
        '''
            Removes tag from the index.

            @param tag: Tag instance to remove 
            @type tag: Tag
        '''
        self._tags.remove(tag)
        self._tag_names.remove(tag.name)

    def rename_tag(self, old_tag, new_tag):
        '''
            Change the name of the tag given by old_tag to name given by new_tag

            @param old_tag:
            @type old_tag: str

            @param new_tag:
            @type new_tag: str
        '''
        if not self.get_tag(old_tag.name):
            raise VHFSException('No tag %s in MetaDataManager' % old_tag)
        self._tags[self._tags.index(old_tag)] = new_tag
        self._tag_names[self._tag_names.index(old_tag.name)] = new_tag.name

    def add_attr(self, attr):
        if not self.is_attribute(attr.key):
            self._attrs.append(attr)
            self._attr_keys.append(attr.key)

    def refresh_tags(self):
        self._tags      = models.Tag.query().all()
        self._tag_names = [t.name for t in self._tags]

    def refresh_attrs(self):
        self._attrs = models.Attribute.query().group_by(models.Attribute.key).all()
        self._attr_keys = [a.key for a in self._attrs] 
        self._attr_keys += models.File.table.columns.keys()

    def is_tag(self, name):
        return True if name in self._tag_names else False

    def is_attribute(self, name):
        return True if name in self._attr_keys else False

    def is_namespace(self, name):
        return True if name in self._namespaces else False

    def get_types_by_name(name):
        types = []
        possible_classes = ['Attribute', 'Tag', 'Namespace']
        for n in possible_classes:
            to_eval = 'self.is_%s(name)' % n.lower()
            if eval(to_eval):
                types.append(name)
        return types

    def is_operation_of(self, operation, namespace):
        to_eval = 'models.%s.Op' % namespace
        logging.debug(to_eval)
        op = eval(to_eval)
        return [False, True][operation in dir(op)]

    def read_items(self, path):

        path  = self.__prepare_path(path)
        path2 = copy.deepcopy(path)

        node       = path[-1]
        dir_items  = []  
        file_items = []  

        if isinstance(node, FileNode) and node.func_node is None:
            raise VHFSException(msg="Last significant node points to the File %s" \
                      % node.name, err_code = errno.ENOTDIR)

        class_name = node.__class__.__name__[0:-4]
        func_name  = node.func_node.name
        if class_name == 'Namespace':
            class_name = node.name
            func_name  = models.NAMESPACE_METHOD_PREFIX + func_name

        logging.debug('func_name: %s, class_name: %s' % (func_name, class_name))
        func = eval('models.%s.get_operation_by_name(func_name)' % class_name)

        if func is not None and models.OpHelper.get_semantic(func) == models.OpHelper.RETURN_DIRS:
            dir_items = func(node.name, *(node.func_node.arg_list))
            dir_items = [t_ID[0] + item for item in dir_items]
        else:
            q          = self.__get_file_query_filter(path2)
            files      = q.all()
            file_items = [f.name for f in files]

        return file_items + dir_items

    def file_exists(self, path):
        path     = self.__prepare_path(path)
        tmp_path = copy.deepcopy(path)
        tmp_path.filter_func_nodes()
        if not isinstance(tmp_path[-1], FileNode):
            return None
        file_node = tmp_path[-1]
        if file_node.func_node \
            and PathInterpreter(path).get_func_semantic(file_node) == models.OpHelper.RETURN_DIRS:
            return None
        q = self.__get_file_query_filter(path)
        q.filter(models.File.name == file_node.name)
        f = q.first()
        if f:
            return len(f.path)
        else:
            return None

    def dir_exists(self, path):
        path = self.__prepare_path(path)
        #if len(path) > 1:
            #parent = path[-2]
            #if isinstance(parent, TagNode) and (parent.func_node.name \
                #in ['default', 'children']) and node.func_node.name == 'has':
                #parent = self.__mdmgr.get_tag(parent.name)
                #child  = self.__mdmgr.get_tag(node.name)
                #if not parent or not child or child.parent <> parent:
                    #raise VHFSException("Tag %s isn't parent of tag %s" % (parent.name, node.name), \
        #                                err_code = -err_code.ENOENT)
        return True

    def __prepare_path(self, path):
        tmp_path       = yacc.parse(path)
        ambigous_nodes = None
        pr             = PathInterpreter(tmp_path) 
        pr.resolve_ambigous_nodes()
        path           = pr.get_path()
        ambigous_nodes = path.get_nodes_with_subnodes_of_type(AmbigousNode)
        if len(ambigous_nodes):
            raise VHFSException("There is no place for ambigouity yet, ambigous node(s): %s" % `ambigous_nodes`, \
                                err_code = errno.ENOENT)

        tag_nodes = path.get_nodes_with_subnodes_of_type(TagNode)
        for t in tag_nodes:
            if not self.is_tag(t.name):
                raise VHFSException("%s isn't name of a tag" % t.name, err_code = -errno.ENOENT)

        attr_nodes = path.get_nodes_with_subnodes_of_type(AttributeNode)
        for a in attr_nodes:
            if not self.is_attribute(a.name):
                raise VHFSException("%s isn't name of an attribute" % a.name, err_code = -errno.ENOENT)
        return pr.get_path()

    # pr - PathInterpreter instance
    def __get_file_query_filter(self, path):
        q    = models.File.query()
        pr   = PathInterpreter(path)
        path = pr.get_path()
        path.filter_file_nodes()
        for node in path:
            func = pr.get_func_handle(node)
            if pr.get_func_semantic(node) in [models.OpHelper.FILE_RESULTS_FILTER, \
                                              models.OpHelper.SQL_FILTER]:
                if isinstance(node, NamespaceNode):
                    q = func(q, *(node.func_node.arg_list))
                else:
                    q = func(q, node.name, *(node.func_node.arg_list))
        return q
        
