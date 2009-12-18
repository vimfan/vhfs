from .operations import Namespace
from .operations import FileFilter
from .operations import DirentryGenerator

import models as m

class TagDirentryGenerator(DirentryGenerator):

    def __init__(self, context, tag_name, *args, **kw):
        super(TagDirentryGenerator, self).__init__(context, *args, **kw)
        self.tag_name = tag_name

class FilterFilesByTag(FileFilter):
    
    def __init__(self, context, tag_name, *args, **kw):
        super(FileFilterByTag, self).__init__(context, *args, **kw)
        self.tag_name = tag_name
        

class Tag(Namespace):

    class Public:
        '''Pseudo class grouping all public methods for the Tag namespace'''


        class Children(TagDirentryGenerator):

            def generate_direntries(self):
                '''
                Returns children of C{tag_name}
                '''
                tag = Tag.get_by(name = self.tag_name)
                context.out = [item.name for item in tag.children_]


        class Descendants(TagDirentryGenerator):

            def generate_direntries(self):
                '''
                Returns descendants of a given tag.
                '''
                pass


        class Parent(TagDirentryGenerator):
            
            def generate_direntries(self):
                '''
                Return parent tag of given tag.
                '''
                pass


        class Ancestors(TagDirentryGenerator):
            
            def generate_direntries(self):
                '''
                Return ancestors of given tag.
                '''
                pass


        class Siblings(TagDirentryGenerator):
            
            def generate_direntries(self):
                '''
                Return siblings of given tag.
                '''
                pass


        class Class:
            '''
            Pseudo class grouping all public class methods
            '''

            
            class All(TagDirentryGenerator):
                '''
                Prepare all indexed tags
                '''
                def generate_direntries(self):
                    self.context.out = [item.name for item in m.Tag.query.all()]

            
            class Any(TagDirentryGenerator):
                '''
                Filter only files which has at least one tag.
                '''
                def generate_direntries(self):
                    self.context.out = [item.name for item in m.Tag.query.all()]


            class Like(TagDirentryGenerator):
                '''
                Prepare all tags which names are like pattern.
                
                    examples: 
                    
                    - @Tag.like:'mus%' satisfies tags with names:
                        - 'music'
                        - 'musician'
                        - 'muse'
                    so:
                    
                    ls @Tag.like:'mus%'
                    @music @musician @muse
                '''
                def generate_direntries(self):
                    self.context.out = []

    class Private:
        '''
        Pseudo class grouping all private methods for the Tag namespace
        '''

        @staticmethod
        def _descendants(tag_name):
            '''
            Returns all descendants of tag given by tag_name. This operation
            is helper for other like: Tag.Private.has, Tag.Public.descendants
            '''
            root = m.Tag.get_by(name=tag_name)
            descs = [root]
            for d in descs:
                descs.extend( d.children_ )
            return descs

        class Has(FilterFilesByTag):

            def filter_files(self):
                '''
                Filter files which has tag with name given by tag_name.
                '''
                descendants = Tag.Private._descendants(self.tag_name)
                context.query.filter(m.File.tags.any(
                    m.Tag.name.in_([d.name for d in descendants])))
 
                      
        class Default(Has)
            '''
            Implements default operation for Tag, i.e. operation when
            invocation is like: /@tagname.

            By default it invokes children operation.

            '''
            pass


        class Negation(FilterFilesByTag)
            '''
            Implements negation operator. E.g.:
                - /not @jazz, 
                - /not@music
            '''
            def filter_files(self):
                self.context.query.filter( 
                    not_(
                        m.File.tags.any( 
                            m.Tag.name.in_( [d.name for d in descs] ))))


