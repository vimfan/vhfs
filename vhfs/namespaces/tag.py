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

            @param context: Current context
            @type context: C{Context}
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

        @semantic(Semantic.FILE_SQL_FILTER)
        def has(context, tag_name):
            '''
            Filter files which has tag with name given by tag_name.
            '''
            descendants = Tag.Private._descendants(tag_name)
            context.query.filter(m.File.tags.any(
                m.Tag.name.in_([d.name for d in descendants])))
        
        @semantic(Semantic.FILE_SQL_FILTER)
        def default(context, tag_name):
            '''
            Implements default operation for Tag, i.e. operation when
            invocation is like: /@tagname.

            By default it invokes children operation.

            @param context: Current context
            @param tag_name: Name of the tag
            '''
            Tag.Public.children(context, tag_name)

        @semantic(Semantic.FILE_SQL_FILTER)
        def negation(context, tag_name):
            '''
            Implements negation operator. E.g.:
                - /not @jazz, 
                - /not@music
            '''
            context.query.filter( \
                not_(
                    m.File.tags.any( \
                        m.Tag.name.in_( [d.name for d in descs] ))))


