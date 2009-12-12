from .operations import Namespace
from .operations import semantic
from .operations import Semantic

import models as m

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

 
