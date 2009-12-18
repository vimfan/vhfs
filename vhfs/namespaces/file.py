from .operations import Namespace
from .operations import DirentryGenerator
from .operations import AttributeFilter
from .operations import KeyNodeCapable

import models as m

class FileDirentryGenerator(DirentryGenerator):
    
    def __init__(self, context, file_name, *args, **kw):
        super(FileDirentryGenerator, self).__init__(context, *args, **kw)
        self.file_name = file_name

class File(Namespace):

    #def transformed_name(self, path):
        #ret = os.path.basename(path) 
        #ret = ret.split('.')
        #ret = '.'.join(['_'.join(ret[0:-1]), 'i' + `self.id`, ret[-1]])
        #return ret
    
    class Private:

        class Default(FileDirentryGenerator):
            
            def __init__(self, *args, **kw):
                super(Default, self).__init__(*args, **kw)
                self._meta = File.Public.Meta(*args, **kw)

            def generate_direntries(self):
                self._meta.execute()

        #class CheckExistance(context, file_name):
            #f = File.get_by(name = file_name)
            #return (not f is None)

    class Public:

        class Meta(FileDirentryGenerator):

            def __init__(self, *args, **kw):
                super(Meta, self).__init__(*args, **kw)
                self._attributes = File.Public.Attributes(*args, **kw)
                self._tags = File.Public.Tags(*args, **kw)

            def generate_direntries(self):
                dirs = []

                self._tags.execute()
                dirs.extend(self.context.out)

                self._attributes.execute()
                dirs.extend(self.context.out)

                context.out = dirs

        class Attributes(FileDirentryGenerator):

            def generate_direntries(self):
                f = m.File.get_by(name = self.file_name)
                out = ['%s=%s' % (a.key, a.value) for a in f.attributes]
                for k in m.File.table.columns.keys():
                    if not k in ['path', 'name']:
                        out.append('%s=%s' % (k, eval('f.%s' % k)))
                self.context.out = out

        class Tags(FileDirentryGenerator):

            def generate_direntries(self):
                f = m.File.get_by(name = file_name)
                self.context.out = [t.name for t in f.tags]


