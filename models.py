from meta_data_manager import MetaDataManager
from elixir import *
from sqlalchemy.sql import and_, or_, not_

import os

NAMESPACE_METHOD_PREFIX = '_class_'

class Namespace:
    def repr(self):
        return ('<# %s' % self.___class__.__name__) + ' = ' + `self.to_dict()` + ' #>'
    
class Tag(Entity, Namespace):
    name = Field(Unicode(50))

    files = ManyToMany('File')
    parent = ManyToOne('Tag')
    children_ = OneToMany('Tag')

    def __repr__(self):
        return super(Tag, self).repr() 


class Attribute(Entity, Namespace):
    key = Field(Unicode(30))
    value = Field(Text)
    files = ManyToMany('File')
    
    def __repr__(self):
        return super(Attribute, self).repr() 



class File(Entity, Namespace):
    path = Field(Unicode(255))
    name = Field(Unicode(255))
    tags = ManyToMany('Tag')
    attributes = ManyToMany('Attribute')

    def __repr__(self):
        return super(File, self).repr() 

class Func(Namespace):
    pass
