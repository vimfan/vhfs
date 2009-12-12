from .operations import Namespace
from .operations import semantic
from .operations import Semantic

import models as m

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
            we're using glob() SQLite builtin function.
            '''
            if Attribute.is_inherent_attr(attr_key):
                context.query.filter(eval('m.File.%s' % attr_key).glob(pattern))
            else:
                context.query.filter(m.File.attributes.any( \
                    m.Attribute.value.op('glob')(pattern)))

        @semantic(Semantic.FILE_SQL_FILTER)
        def assign(context, attr_key, attr_val):
            return cls.equal(context, attr_key, attr_val)
    

