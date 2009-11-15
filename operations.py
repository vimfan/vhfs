import models as m

NAMESPACE_METHOD_PREFIX = '_class_'

class SemanticEnum:
    FILE_RESULT_FILTER = 1
    SQL_FILTER         = 2
    DIRENTRY_GENERATOR = 3
    DIRENTRY_FILTER    = 4

def semantic(cls, name):
    '''
        Returns semantic of the operation given by name. Operation must be 
        supported by class given by cls.

        @param cls: Class of operation
        @type: class

        @return: Semantic indicator
        @rtype: SemanticEnum
    '''
    pass

def eval(context, cls, name, *args):
    pass

class Namespace:
    def ivoke_private_class_method()
        pass

    def ivoke_public_class_method()
        pass

    def ivoke_private_instance_method():
        pass

    def ivoke_public_instance_method():
        pass

class Tag:

    class Public:
       
        @staticmethod
        def negation(context, tag_name):
            root = m.Tag.get_by(name = tag_name)
            descs = [root]
            for d in descs:
                descs.extend(d.children_)
            context.query.filter( \
                not_(
                    m.File.tags.any( \
                        m.Tag.name.in_( [d.name for d in descs] ))))

    class Private:

        @staticmethod
        def has(context, tag_name):
            root = m.Tag.get_by(name=tag_name)
            descs = [root]
            for d in descs:
                descs.extend( d.children_ )
            context.query.filter(m.File.tags.any(m.Tag.name.in_([d.name for d in descs])))
        

        @staticmethod
        def default(context, tag_name):
            cls.children(context, tag_name)

        @staticmethod
        def children(context, tag_name):
            tag = Tag.get_by(name = tag_name)
            context.out = [item.name for item in tag.children_]
            
        @staticmethod
        def descendants(context, tag_name):
            pass

        @staticmethod
        def parent(context, tag_name):
            pass

        @staticmethod
        def ancestors(context, tag_name):
            pass

        @staticmethod
        def siblings(context, tag_name):
            pass

        @staticmethod
        def _class_all(context, pattern):
            pass

        @staticmethod
        def _class_any(name, pattern):
            pass

        # e.g. /@Tag.like:'mus%'
        # returns all tags with name like mus%
        @staticmethod
        def _class_like(name, pattern):
            pass

class Attribute:
    
        @staticmethod
        def __is_inherent_attr(attr_key):
            return [False, True][attr_key in File.table.columns.keys()]

        @staticmethod
        def default(attr_key):
            return Attribute.Op.values(attr_key)
        
        # return list of directories: key = val
        @staticmethod
        def values(attr_key):
            return [str('%s=%s') % (attr.key, attr.value) for attr in m.Attribute.context.filter(m.Attribute.key == attr_key).group_by(m.Attribute.value).all()]


        @staticmethod
        def lt(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key) < value)
            else:
                return context.filter(File.attributes.any( \
                    and_(m.Attribute.value < value, m.Attribute.key == attr_key)))

        @staticmethod
        def le(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key) <= value)
            else:
                return context.filter(File.attributes.any( \
                    and_(m.Attribute.value <= value, m.Attribute.key == attr_key)))

        @staticmethod
        def gt(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key) > value)
            else:
                return context.filter(File.attributes.any( \
                    and_(Attribute.value > value, Attribute.key == attr_key)))

        @staticmethod
        def ge(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key) >= value)
            else:
                return context.filter(File.attributes.any( \
                    and_(Attribute.value >= value, Attribute.key == attr_key)))

        @staticmethod
        def eq(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key) == value)
            else:
                return context.filter(File.attributes.any( \
                    and_(Attribute.value == value, Attribute.key == attr_key)))

        @staticmethod
        def neq(context, attr_key, value):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key != value))
            else:
                return context.filter(File.attributes.any( \
                    and_(Attribute.value != value, Attribute.key == attr_key)))

        @staticmethod
        def like(context, attr_key, pattern):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key).like(pattern))
            else:
                return context.filter(File.attributes.any(Attribute.value.like(pattern)))

        # FIXME: glob is not equivalent of regexp
        @staticmethod
        def regexp(context, attr_key, pattern):
            if cls.__is_inherent_attr(attr_key):
                return context.filter(eval('File.%s' % attr_key).glob(pattern))
            else:
                return context.filter(File.attributes.any( \
                    Attribute.value.op('glob')(pattern)))

        @staticmethod
        def negation(context, attr_key):
            if cls.__is_inherent_attr(attr_key):
                return context.limit(0)
            else:
                return context.filter(
                    not_(File.attributes.any( \
                        (Attribute.key == attr_key ))))

        @staticmethod
        def _class_assign(context, attr_key, attr_val):
            return cls.equal(context, attr_key, attr_val)
    
class File:

    def transformed_name(self, path):
        ret = os.path.basename(path) 
        ret = ret.split('.')
        ret = '.'.join(['_'.join(ret[0:-1]), 'i' + `self.id`, ret[-1]])
        return ret
    
        @staticmethod
        def default(file_name):
            return cls.meta(file_name)

        @staticmethod
        def meta(file_name):
            dirs = []
            dirs.extend(cls.attributes(file_name))
            dirs.extend(cls.tags(file_name))
            return dirs

        @staticmethod
        def attributes(file_name):
            f = File.get_by(name = file_name)
            out = ['%s=%s' % (a.key, a.value) for a in f.attributes]
            for k in File.table.columns.keys():
                if not k in ['path', 'name']:
                    out.append('%s=%s' % (k, eval('f.%s' % k)))
            return out

        @staticmethod
        def tags(file_name):
            f = File.get_by(name = file_name)
            return [t.name for t in f.tags]

class Func:

    class Public:

        @staticmethod
        def _class_limit(context, limit, offset = 0):
            limit  = int(limit)
            offset = int(offset)
            if limit > 0:
                context = context.limit(limit)
                return cls._class_offset(context, offset)
            else:
                return context

        @staticmethod
        def _class_offset(context, value):
            value = int(value)
            return context.offset(value)

        @staticmethod
        def _class_order(*arg):
            pass

        @staticmethod
        def _class_like(pattern):
            pass

        @staticmethod
        def _class_regexp(pattern):
            pass
 
