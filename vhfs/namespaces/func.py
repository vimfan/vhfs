from .operations import Namespace
from .operations import DirentryFilter
from .operations import SQLFilter

import models as m

class Func(Namespace):

    class Public:

        class Class:

            class Limit(SQLFilter, DirentryFilter):

                def __init__(self, limit, offset = 0, *args, **kw)
                    SQLFilter.__init__(self, *args, **kw)
                    DirentryFilter.__init__(self, *args, **kw)
                    self.limit = int(limit)
                    self.offset = int(offset)

                def filter_by_sql(self):
                    if self.limit > 0:
                        q = self.context.query 
                        q = q.limit(limit)
                        Func.Public.Class.Offset(self.offset, self.context).filter_by_sql()

            class Offset(SQLFilter, DirentryFilter):

                def __init__(self, offset, *args, **kw)
                    SQLFilter.__init__(self, *args, **kw)
                    DirentryFilter.__init__(self, *args, **kw)
                    self.offset = int(offset)

                def filter_by_sql(self):
                    if self.offset > 0:
                        q = self.context.query
                        q = q.offset(self.offset)

            class Order(SQLFilter, DirentryFilter):

                def __init__(self, *args, **kw)
                    SQLFilter.__init__(self, *args, **kw)
                    DirentryFilter.__init__(self, *args, **kw)
                    self.offset = int(offset)
 
            #@semantic(Semantic.DIRENTRY_FILTER)
            #def like(context, pattern):
                #pass
                
            #@semantic(Semantic.DIRENTRY_FILTER)
            #def regexp(context, pattern):
                #pass
        
    #class Reductor:
        
        #@staticmethod
        #def limit(nodes):
            #return nodes[-1]

        #@staticmethod
        #def order(nodes):
            #return nodes[-1]
 
