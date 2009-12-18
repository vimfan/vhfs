from .operations import Namespace
from .operations import FileFilter
from .operations import AttributeFilter
from .operations import DirentryGenerator
from .operations import KeyNodeCapable

import models as m

class FilterFilesByAttribute(FileFilter):

    def __init__(self, context, attr_key, attr_value, *args, **kw):
        super(FilterFilesByAttribute, self).__init__(context, *args, **kw)
        self.attr_key = attr_key
        self.attr_value = attr_value

class FilterFilesByAttributeWithOperand(FilterFilesByAttribute):

    def filter_with_operand(self, operand):
        if Attribute.is_inherent_attr(self.attr_key):
            self.context.query.filter(
                eval('m.File.%(key)s %(operand)s self.attr_value' 
                    % 'key' : self.attr_key, 'operand' : operand))
        else:
            self.context.query.filter(m.File.attributes.any( 
                and_(eval('m.Attribute.value %s self.attr_value' % operand}, 
                    m.Attribute.key == self.attr_key)))

class AttributeDirentryGenerator(DirentryGenerator):
    
    def __init__(self, context, attr_key, *args, **kw):
        super(AttributeDirentryGenerator, self).__init__(context, *args, **kw)
        self.attr_key = attr_key


class Attribute(Namespace):

    @staticmethod
    def is_inherent_attr(attr_key):
        return attr_key in m.File.table.columns.keys()

    class Private:          

        class Negation(FilterFilesByAttribute)

            def filter_files(self):
                if Attribute.is_inherent_attr(self.attr_key):
                    context.query.limit(0)
                else:
                    context.query.filter(
                        not_(
                            m.File.attributes.any( 
                                (m.Attribute.key == attr_key ))))

                
        class Default(Public.Values):
            pass
 
            #def __init__(self, *args, **kw):
                #super(Default, self).__init__(*args, **kw)
                #self._values = Attribute.Public.Values(*args, **kw)
            
            #def generate_direntries(self):
                #self._values.execute()


        class Assign(FilterFilesByAttribute, AttributeCreator, AssociationCreator)
            
            def __init__(self, *args, **kw):
                FilterFilesByAttribute.__init__(self, *args, **kw)
                AttributeCreator.__init__(self, *args, **kw)
                AssociationCreator.__init__(self, *args, **kw)

                self._equal = Attribute.Public.Eq(*args, **kw)

            def execute(self):
                pass

            def filter_files(self):
                self._equal.filter_files()

    class Public:
                
        class Values(AttributeDirentryGenerator):

            def generate_direntries(self):
                pattern = '%(key)s=%(value)s' 
                attributes = m.Attribute.query.filter(
                                m.Attribute.key == attr_key).group_by(
                                    m.Attribute.value).all():
                f = lambda attr: pattern % {'key' : str(attr.key), 'value' : str(attr.value)
                self.context.out = map(f, attributes)
                    
        class Lt(FilterFilesByAttributeWithOperand):

            def filter_files(self):
                self.filter_with_operand('<')
                    
        class Le(FilterFilesByAttributeWithOperand):

            def filter_files(self):
                self.filter_with_operand('<=')
 
        class Gt(FilterFilesByAttributeWithOperand):

            def filter_files(self):
                self.filter_with_operand('>')

        class Ge(FilterFilesByAttributeWithOperand):

            def filter_files(self):
                self.filter_with_operand('>=')

        class Eq(FilterFilesByAttributeWithOperand, AttributeCreator, AssociationCreator):
            
            def filter_files(self):
                self.filter_with_operand('==')

        class Neq(FilterFilesByAttributeWithOperand):
            
            def filter_files(self):
                self.filter_with_operand('!=')


        class Like(FilterFilesByAttribute):
            
            def filter_files(self):
                if Attribute.is_inherent_attr(self.attr_key):
                    context.query.filter(eval('m.File.%s' % self.attr_key).like(self.attr_value))
                else:
                    context.query.filter(m.File.attributes.any(
                        m.Attribute.value.like(self.attr_value)))

        class Regexp(FilterFilesByAttribute):
            '''
            Operation semantically similar to regexp, but instead of regexp()
            we're using glob() SQLite builtin function.
            '''

            def filter_files(self):
                if Attribute.is_inherent_attr(self.attr_key):
                    context.query.filter(eval('m.File.%s' % attr_key).glob(self.attr_value))
                else:
                    context.query.filter(m.File.attributes.any( \
                        m.Attribute.value.op('glob')(self.attr_value)))


