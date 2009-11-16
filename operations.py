import models as m
import sys
import re

class Semantic:

    FILE_SQL_FILTER    = 0x0001 
    '''@cvar: When operation adds some filtering to query on File table'''
    SQL_FILTER         = 0x0002
    '''@cvar: General SQL filtering operations like: limit, offset etc.'''
    DIRENTRY_GENERATOR = 0x0004
    '''@cvar: This kind of operations don't modify context.query'''
    DIRENTRY_FILTER    = 0x0008
    '''@cvar: Filter which can be applied for C{context.out} rather in contradiction
       to SQL_FILTER which can be only applied to C{context.query}'''
    REDUCIBLE_FILTER   = 0x0020
    '''@cvar: Some filters may be reducted to one filter, e.g. 
       /@Func.limit:10/@Func.limit:20 => /@Func.limit:20'''

    def __init__(self, flags):
        possible_flags = ['FILE_SQL_FILTER', 'SQL_FILTER', 
                                 'DIRENTRY_GENERATOR', 'DIRENTRY_FILTER', 
                                 'REDUCIBLE_FILTER']
        for item in possible_flags: 
            eval('self.%(field_name)s = (Semantic.%(flag)s & flags) != 0 ' \
                % {'field_name' : item.lower(), 'flag' : item})

class Registry:
    _entries = []

    class Entry:
        pass

    class OperationEntry(Entry):

        def __init__(self, operation, semantic_flags):
            self.operation = operation
            self.semantic = Semantic(semantic_flags)

    @classmethod
    def append_operation(cls, operation, semantic):
        '''
        Add new entry to the registry.
        '''
        cls._entries.append(cls.OperationEntry(operation, semantic))

    @classmethod
    def semantic(cls, operation):
        '''
        Returns semantic of the operation given by E{operation}. 

        @return: Semantic indicator
        @rtype: Semantic
        '''
        for entry in cls.entries:
            if entry.operation == operation:
                return entry.semantic

def semantic(semantic_indicator = Semantic.UNKNOWN):
    '''
    Generates decorator function for operations. Every decorator generated by
    its wraps method with staticmethod decorator.

    @param semantic_indicator: Parameter indicating semantic.
    @type semantic_indicator: Semanticfield
    '''
    decorator_name = 'semantic_' + str(semantic_indicator)
    exec('''
def %s(f):
    i = 1
    trace = []
    trace.insert(0, f.func_name)
    while True:
        stair = sys._getframe(i).f_code.co_name
        if re.search("module", stair):
            break
        trace.insert(0, stair)
        i += 1
<<<<<<< HEAD:operations.py
    func_name = ".".join(trace)
    Registry.append_operation(func_name, %s)
=======
    operation_name = ".".join(trace)
    Registry.append_entry(operation_name, %s)
>>>>>>> f95c3d44cdc67d595af3ad0d4278f02fd0bd5378:operations.py
    return staticmethod(f)
''' % (decorator_name, semantic_indicator))
    return eval(decorator_name)

# bo patient with using eval(), builtin function with that name
# is very often used and we don't want to override it
def run(context, cls, name, *args):
    pass

class Namespace:
    pass

class Tag(Namespace):

    class Public:
        '''Pseudo class grouping all public methods for the Tag namespace'''

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def children(context, tag_name):
            '''
            Returns children of C{tag_name}

            @param tag_name: Name of the tag.
            @type tag_name: C{str}
            '''
            tag = Tag.get_by(name = tag_name)
            context.out = [item.name for item in tag.children_]
            
        @semantic(Semantic.FILE_SQL_FILTER)
        def descendants(context, tag_name):
            '''
            Returns descendants of C{tag_name}

            @param tag_name: Name of the tag.
            @type tag_name: C{str}
            '''
            pass

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def parent(context, tag_name):
            pass

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def ancestors(context, tag_name):
            pass

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def siblings(context, tag_name):
            pass

        class Class:
            '''
            Pseudo class grouping all public class methods
            '''

            @semantic(Semantic.DIRENTRY_GENERATOR)
            def all(context, pattern):
                '''
                Prepare all indexed tags
                '''
                pass

            @semantic(Semantic.FILE_SQL_FILTER)
            def any(name, pattern):
                '''
                Filter only files which has some tags.
                '''
                pass

            @semantic(Semantic.FILE_SQL_FILTER)
            def like(name, pattern):
                '''
                Prepare all tags which names are like pattern.
                
                    examples: 
                    
                    - @Tag.like:'mus%' satisfies tags with names:
                        - 'music'
                        - 'musician'
                        - 'muse'
                '''
                pass

    class Private:
        '''
        Pseudo class grouping all private methods for the Tag namespace
        '''

        @semantic(Semantic.FILE_SQL_FILTER)
        def has(context, tag_name):
            '''
            Filter files which has tag with name given by tag_name.
            '''
            root = m.Tag.get_by(name=tag_name)
            descs = [root]
            for d in descs:
                descs.extend( d.children_ )
            context.query.filter(m.File.tags.any(
                m.Tag.name.in_([d.name for d in descs])))
        
        @semantic(Semantic.FILE_SQL_FILTER)
        def default(context, tag_name):
            Tag.Public.children(context, tag_name)

        @semantic(Semantic.FILE_SQL_FILTER)
        def negation(context, tag_name):
            root = m.Tag.get_by(name = tag_name)
            descs = [root]

            for d in descs:
                descs.extend(d.children_)

            context.query.filter( \
                not_(
                    m.File.tags.any( \
                        m.Tag.name.in_( [d.name for d in descs] ))))
    
class Attribute(Namespace):

    @staticmethod
    def is_inherent_attr(attr_key):
        return [False, True][attr_key in m.File.table.columns.keys()]

    class Private:          

        @semantic(Semantic.FILE_SQL_FILTER)
        def negation(context, attr_key):
            if Attribute.is_inherent_attr(attr_key):
                context.query.limit(0)
            else:
                context.query.filter(
                    not_(m.File.attributes.any( \
                        (m.Attribute.key == attr_key ))))

        @semantic(Semantic.FILE_SQL_FILTER)
        def default(context, attr_key):
            context.out = m.Attribute.Public.values(context, attr_key)

    class Public:
                
        @semantic(Semantic.DIRENTRY_GENERATOR)
        def values(context, attr_key):
            context.out = [str('%s=%s') % (attr.key, attr.value) 
                for attr in m.Attribute.query.filter(
                    m.Attribute.key == attr_key).group_by(
                        m.Attribute.value).all()]

        @semantic(Semantic.FILE_SQL_FILTER)
        def lt(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key) < value)
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value < value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def le(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key) <= value)
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value <= value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def gt(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key) > value)
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value > value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def ge(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key) >= value)
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value >= value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def eq(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key) == value)
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value == value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def neq(context, attr_key, value):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key != value))
            else:
                context.query.filter(m.File.attributes.any( \
                    and_(m.Attribute.value != value, 
                         m.Attribute.key == attr_key)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def like(context, attr_key, pattern):
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key).like(pattern))
            else:
                context.query.filter(m.File.attributes.any(
                    m.Attribute.value.like(pattern)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def regexp(context, attr_key, pattern):
            '''
            Operation semantically similar to regexp, but instead of regexp()
            we're using glob() SQLite builtin method.
            '''
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key).glob(pattern))
            else:
                context.query.filter(m.File.attributes.any( \
                    m.Attribute.value.op('glob')(pattern)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def assign(context, attr_key, attr_val):
            return cls.equal(context, attr_key, attr_val)
    
class File(Namespace):

    def transformed_name(self, path):
        ret = os.path.basename(path) 
        ret = ret.split('.')
        ret = '.'.join(['_'.join(ret[0:-1]), 'i' + `self.id`, ret[-1]])
        return ret
    
    class Private:

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def default(context, file_name):
            context.out = File.Public.meta(file_name)

    class Public:

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def meta(context, file_name):
            dirs = []
            dirs.extend(cls.attributes(file_name))
            dirs.extend(cls.tags(file_name))
            context.out = dirs

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def attributes(context, file_name):
            f = File.get_by(name = file_name)
            out = ['%s=%s' % (a.key, a.value) for a in f.attributes]
            for k in File.table.columns.keys():
                if not k in ['path', 'name']:
                    out.append('%s=%s' % (k, eval('f.%s' % k)))
            context.out = out

        @semantic(Semantic.DIRENTRY_GENERATOR)
        def tags(context, file_name):
            f = File.get_by(name = file_name)
            context.out = [t.name for t in f.tags]

class Func(Namespace):

    class Public:

        class Class:

            @semantic(Semantic.SQL_FILTER)
            def limit(context, limit, offset = 0):
                limit  = int(limit)
                offset = int(offset)
                if limit > 0:
                    context.query = context.query.limit(limit)
                    Func.Public.Class.offset(context, offset)
 
            @semantic(Semantic.SQL_FILTER)
            def offset(context, value):
                value = int(value)
                context.query.offset(value)
 
            @semantic(Semantic.FILE_SQL_FILTER | Semantic.DIRENTRY_FILTER)
            def order(context, *args):
                if len(args) == 0:
                    # perform some sorting on context.out
                    pass
                    # sort output directory
                else:
                    # sql query
                    pass
 
            @semantic(Semantic.DIRENTRY_FILTER)
            def like(context, pattern):
                pass
                
            @semantic(Semantic.DIRENTRY_FILTER)
            def regexp(context, pattern):
                pass
 
