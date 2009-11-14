from meta_data_manager import MetaDataManager
from elixir import *
from sqlalchemy.sql import and_, or_, not_

import os

NAMESPACE_METHOD_PREFIX = '_class_'

class OpHelper:
    
    FILE_RESULTS_FILTER = 0
    RETURN_DIRS         = 1
    SQL_FILTER          = 2

    __operation_types = {}

    @classmethod
    def get_semantic(cls, operation):
        return OpHelper.__operation_types[operation]

    @classmethod
    def assign_semantic(cls, operation, type):
        OpHelper.__operation_types[operation] = type

class Namespace:
    def repr(self):
        return ('<# %s' % self.___class__.__name__) + ' = ' + `self.to_dict()` + ' #>'
    
    @classmethod
    def get_operation_by_name(cls, name):
        func = eval('%s.Op.%s' % (cls.__name__, name))
        return func

class Tag(Entity, Namespace):
    name      = Field(Unicode(50))

    files     = ManyToMany('File')
    parent    = ManyToOne('Tag')
    children_ = OneToMany('Tag')

    def __repr__(self):
        return super(Tag, self).repr() 

    class Op(OpHelper):
        
        @classmethod
        def init_types(cls):
            Tag.Op.assign_semantic(Tag.Op.default,     Tag.Op.RETURN_DIRS)
            Tag.Op.assign_semantic(Tag.Op.children,    Tag.Op.RETURN_DIRS)
            Tag.Op.assign_semantic(Tag.Op.descendants, Tag.Op.RETURN_DIRS)
            Tag.Op.assign_semantic(Tag.Op.ancestors,   Tag.Op.RETURN_DIRS)
            Tag.Op.assign_semantic(Tag.Op.siblings,    Tag.Op.RETURN_DIRS)

            Tag.Op.assign_semantic(Tag.Op.has,         Tag.Op.FILE_RESULTS_FILTER)
            Tag.Op.assign_semantic(Tag.Op.negation,    Tag.Op.FILE_RESULTS_FILTER)

            Tag.Op.assign_semantic(Tag.Op._class_any,   Tag.Op.FILE_RESULTS_FILTER)
            Tag.Op.assign_semantic(Tag.Op._class_like,  Tag.Op.RETURN_DIRS)
            Tag.Op.assign_semantic(Tag.Op._class_all,   Tag.Op.RETURN_DIRS)

        @classmethod
        def negation(cls, query, tag_name):
            root = Tag.get_by(name=tag_name)
            descs = [root]
            for d in descs:
                descs.extend(d.children_)
            return query.filter( \
                not_(
                    File.tags.any( \
                        Tag.name.in_( [d.name for d in descs] ))))

        @classmethod
        def has(cls, query, tag_name):
            root = Tag.get_by(name=tag_name)
            descs = [root]
            for d in descs:
                descs.extend(d.children_)
            return query.filter(File.tags.any(Tag.name.in_([d.name for d in descs])))
        

        # e.g. /music:
        @classmethod
        def default(cls, tag_name):
            return Tag.Op.children(tag_name)

        # e.g. /music:children
        # returns list of directories
        @classmethod
        def children(cls, tag_name):
            tag = Tag.get_by(name=tag_name)
            return [item.name for item in tag.children_]
            
        # e.g. /music:descendants
        # returns list of directories
        @classmethod
        def descendants(cls, tag_name):
            pass

        # e.g. /music:parents
        # returns list of directories
        @classmethod
        def parent(cls, tag_name):
            pass

        # e.g. /music:ancestors
        # returns list of directories
        @classmethod
        def ancestors(cls, tag_name):
            pass

        # e.g. /music:ancestors
        @classmethod
        def siblings(cls, tag_name):
            pass

        # /@Tag.all return dirs with all tags
        @classmethod
        def _class_all(cls, name, pattern):
            pass

        # /@Tag.any filter
        @classmethod
        def _class_any(cls, name, pattern):
            pass

        # e.g. /@Tag.like:'mus%'
        # returns all tags with name like mus%
        @classmethod
        def _class_like(cls, name, pattern):
            pass



Tag.Op.init_types()

class Attribute(Entity, Namespace):
    key   = Field(Unicode(30))
    value = Field(Text)

    files = ManyToMany('File')
    
    def __repr__(self):
        return super(Attribute, self).repr() 


    class Op(OpHelper):

        @classmethod
        def init_types(cls):
            Attribute.Op.assign_semantic(Attribute.Op.default,          Attribute.Op.RETURN_DIRS)
            Attribute.Op.assign_semantic(Attribute.Op.values,           Attribute.Op.RETURN_DIRS)

            Attribute.Op.assign_semantic(Attribute.Op.less_than,        Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.less_or_equal,    Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.greater_or_equal, Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.greater_than,     Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.equal,            Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.not_equal,        Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.like,             Attribute.Op.FILE_RESULTS_FILTER)
            Attribute.Op.assign_semantic(Attribute.Op.regexp,           Attribute.Op.FILE_RESULTS_FILTER)

            Attribute.Op.assign_semantic(Attribute.Op.negation,         Attribute.Op.FILE_RESULTS_FILTER)

            Attribute.Op.assign_semantic(Attribute.Op._class_assign,     Attribute.Op.FILE_RESULTS_FILTER)

        @classmethod
        def __is_inherent_attr(cls, attr_key):
            return [False, True][attr_key in File.table.columns.keys()]

        @classmethod
        def default(cls, attr_key):
            return Attribute.Op.values(attr_key)
        
        # return list of directories: key = val
        @classmethod
        def values(cls, attr_key):
            return [str('%s=%s') % (attr.key, attr.value) for attr in Attribute.query.filter(Attribute.key == attr_key).group_by(Attribute.value).all()]


        @classmethod
        def less_than(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key) < value)
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value < value, Attribute.key == attr_key)))

        @classmethod
        def less_or_equal(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key) <= value)
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value <= value, Attribute.key == attr_key)))

        @classmethod
        def greater_than(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key) > value)
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value > value, Attribute.key == attr_key)))

        @classmethod
        def greater_or_equal(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key) >= value)
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value >= value, Attribute.key == attr_key)))

        @classmethod
        def equal(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key) == value)
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value == value, Attribute.key == attr_key)))

        @classmethod
        def not_equal(cls, query, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key != value))
            else:
                return query.filter(File.attributes.any( \
                    and_(Attribute.value != value, Attribute.key == attr_key)))

        @classmethod
        def like(cls, query, attr_key, pattern):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key).like(pattern))
            else:
                return query.filter(File.attributes.any(Attribute.value.like(pattern)))

        # FIXME: glob is not equivalent of regexp
        @classmethod
        def regexp(cls, query, attr_key, pattern):
            if cls.__is_inherent_attr(attr_key):
                return query.filter(eval('File.%s' % attr_key).glob(pattern))
            else:
                return query.filter(File.attributes.any( \
                    Attribute.value.op('glob')(pattern)))

        @classmethod
        def negation(cls, query, attr_key):
            if cls.__is_inherent_attr(attr_key):
                return query.limit(0)
            else:
                return query.filter(
                    not_(File.attributes.any( \
                        (Attribute.key == attr_key ))))

        @classmethod
        def _class_assign(cls, query, attr_key, attr_val):
            return cls.equal(query, attr_key, attr_val)

Attribute.Op.init_types()

class File(Entity, Namespace):
    path       = Field(Unicode(255))
    name       = Field(Unicode(255))
    tags       = ManyToMany('Tag')
    attributes = ManyToMany('Attribute')

    def __repr__(self):
        return super(File, self).repr() 

    def transformed_name(self, path):
        ret = os.path.basename(path) 
        ret = ret.split('.')
        ret = '.'.join(['_'.join(ret[0:-1]), 'i' + `self.id`, ret[-1]])
        return ret

    def get_tag_by_name(self, name):
        for t in self.tags:
            if t.name == name:
                return t

    def get_attr_by_key(self, key):
        for a in self.attributes:
            if a.key == key:
                return a

    def get_attr_by_key_and_val(self, key, val):
        for a in self.attributes:
            if a.key == key and a.value == val:
                return a

    
    class Op(OpHelper):

        @classmethod
        def init_types(cls):
            File.Op.assign_semantic(File.Op.default,    File.Op.RETURN_DIRS)
            File.Op.assign_semantic(File.Op.attributes, File.Op.RETURN_DIRS)
            File.Op.assign_semantic(File.Op.tags,       File.Op.RETURN_DIRS)
            #File.Op.assign_semantic(File.Op.unindex,    File.Op.RETURN_DIRS)

        @classmethod
        def default(cls, file_name):
            return cls.meta(file_name)

        @classmethod
        def meta(cls, file_name):
            dirs = []
            dirs.extend(cls.attributes(file_name))
            dirs.extend(cls.tags(file_name))
            return dirs

        @classmethod
        def attributes(cls, file_name):
            f = File.get_by(name = file_name)
            out = ['%s=%s' % (a.key, a.value) for a in f.attributes]
            for k in File.table.columns.keys():
                if not k in ['path', 'name']:
                    out.append('%s=%s' % (k, eval('f.%s' % k)))
            return out

        @classmethod
        def tags(cls, file_name):
            f = File.get_by(name = file_name)
            return [t.name for t in f.tags]

File.Op.init_types()

class Func(Namespace):

    class Op(OpHelper):

        @classmethod
        def init_types(cls):
            Func.Op.assign_semantic(Func.Op._class_limit,  Func.Op.SQL_FILTER)
            Func.Op.assign_semantic(Func.Op._class_order,  Func.Op.SQL_FILTER)
            Func.Op.assign_semantic(Func.Op._class_like,   Func.Op.SQL_FILTER)
            Func.Op.assign_semantic(Func.Op._class_regexp, Func.Op.SQL_FILTER)
            
        @classmethod
        def _class_limit(cls, query, limit, offset = 0):
            limit  = int(limit)
            offset = int(offset)
            if limit > 0:
                query = query.limit(limit)
                return cls._class_offset(query, offset)
            else:
                return query

        @classmethod
        def _class_offset(cls, query, value):
            value = int(value)
            return query.offset(value)

        @classmethod
        def _class_order(cls, *arg):
            pass

        @classmethod
        def _class_like(cls, pattern):
            pass

        @classmethod
        def _class_regexp(cls, pattern):
            pass
    
Func.Op.init_types()
