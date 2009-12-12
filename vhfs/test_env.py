from models import *
from elixir import *

metadata.bind = 'sqlite:///vhfs.sqlite'
metadata.bind.echo = True 

setup_all()
create_all()

import parser
import interpreter
import copy

import nodes

#path = vhfs_parser.yacc.parse('/music:/c:children/bitrate:values/:limit 120#int/some_tag:/b/tag#tag:')
s = '/@tag./@music./@jazz/@rock/@bitrate<50/@mod_dtime<10:00'
path = nodes.PathNode(s)
#path = parser.yacc.parse(path_string)

#pr = path_interpreter.PathInterpreter(path)

#print str(pr)

#print list(path)[0:-1]

#pr = path_resolver.PathResolver(path)

#pr = path_resolver.PathResolver(path)
#pr.resolve_type_hints()
#print pr
#path = vhfs_parser.yacc.parse('/:limit 5/:limit 1')
##print Path(v) + pr.get_path() 
##pr.resolve_type_hints()
##pr.resolve_ambigous_nodes()
##print Tag.query().all()
##print Attribute.query().all()


#def get_descentents(tag_name):
	#root = Tag.get_by(name=tag_name)
	#descendants = [root]
	#for d in descendants:
		#descendants.extend(d.children_)
	#return descendants

#print get_descentents('tag')


	

#class Test:

	#def __define_method(self, key, val):
		#__skeleton = '''
#def func(cls, arg):
	#print "%s"'''
		#__to_exec = __skeleton % val
		#exec(__to_exec)
		#setattr(Test, key, func)
		#to_eval = '%s = classmethod(func)' % key
		#print to_eval
		#eval(to_eval)

		

	#def __init__(self):
		#__pairs = {
			#'less_than'     : '<',
			#'less_or_equal' : '<=',
			#'grater_than'   : '>',
		#}
		#for __k in __pairs:
			#self.__define_method(__k, __pairs[__k])



#Test()
#Test()
#print dir(Test)
#Test.less_than(1)
#Test.greater_than(1)


import operations
for entry in operations.Registry._entries:
    print entry
