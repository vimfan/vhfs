from .operations import Namespace
from .operations import semantic
from .operations import Semantic

import models as m

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
                else:
                    # sql query
                    pass
 
            @semantic(Semantic.DIRENTRY_FILTER)
            def like(context, pattern):
                pass
                
            @semantic(Semantic.DIRENTRY_FILTER)
            def regexp(context, pattern):
                pass
        
    class Reductor:
        
        @staticmethod
        def limit(nodes):
            return nodes[-1]

        @staticmethod
        def order(nodes):
            return nodes[-1]
 
