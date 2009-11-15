from meta_data_manager import MetaDataManager
from elixir import *
from sqlalchemy.sql import and_, or_, not_

import os

class EntityExt:
    def _repr(self):
        return ('<# %s' % self.___class__.__name__) + ' = ' + `self.to_dict()` + ' #>'
    
class Tag(Entity, EntityExt):
    name = Field(Unicode(50))

    files = ManyToMany('File')
    parent = ManyToOne('Tag')
    children_ = OneToMany('Tag')

    def __repr__(self):
        return super(Tag, self)._repr() 

class Attribute(Entity, EntityExt):
    key = Field(Unicode(30))
    value = Field(Text)
    files = ManyToMany('File')
    
    def __repr__(self):
        return super(Attribute, self)._repr() 

class File(Entity, EntityExt):
    path = Field(Unicode(255))
    name = Field(Unicode(255))
    tags = ManyToMany('Tag')
    attributes = ManyToMany('Attribute')

    def get_tag_by_name(self, name):
        for t in self.tags:
            if t.name == name:
                return t

    def get_attr_by_key(self, key):
        for a in self.attributes:
            if a.key == key:
                return a

    def get_attr_by_key_and_val(self, key, val):
        for a in self.attributes:
            if a.key == key and a.value == val:
                return a

    def __repr__(self):
        return super(File, self)._repr() 
