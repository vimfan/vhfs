import datetime
import datatypes.generic

from vhfs_exceptions import *
from nodes import *

tokens = (
    'DELIMITER',
    'ID',
    'FUNC',
    'INTEGER',
    'FILE',
    'REAL',
    'NEGATION',
    'EQUAL',
    'NEQUAL',
    'LT',
    'GT',
    'LE',
    'GE',
    'ARG_SEPARATOR',
    'ARG_SPECIFIER',
    'LIKE',
    'REGEXP',
    'ASSIGN',
    'STRING',
    'DATE',
    'TIME',
    'TYPE_CAST',
    'LPAREN',
    'RPAREN',
    )

# Tokens

# bin_op
t_LT       = r'<'
t_GT       = r'>'
t_LE       = r'<='
t_GE       = r'>='
t_ASSIGN   = r':='

t_ARG_SEPARATOR = r','
t_ARG_SPECIFIER = r':'
t_LPAREN        = r'{'
t_RPAREN        = r'}'
#t_DOT           = r'\.'

# constants
EQUAL_           = '='
NEQUAL_          = '<>'
NEGATION_        = 'Private.negation'
LIKE_            = 'like'
REGEXP_          = 'regexp'
UNSPECIFIED_SYM  = 'default'

t_DELIMITER = r'/'
t_ID        = r'@[a-zA-Z0-9][a-zA-Z0-9_]*' 
RAW_FUNC_SPECIFIER = r'.'
FUNC_SPECIFIER = "\\" + RAW_FUNC_SPECIFIER
t_FUNC      = FUNC_SPECIFIER + r'([a-zA-Z0-9][a-zA-Z0-9_]*)*'
t_TYPE_CAST = r'[a-zA-Z][a-zA-Z0-9_]*'

precedence = (
)

def t_FILE(t):      
    r'[^/,.:#\ ]+\.i\d+\.?[^/,.:#\ ]*' 
    return t

def t_LIKE(t):
    r'[Ll][Ii][Kk][Ee]'
    t.value = LIKE_
    return t

def t_STRING(t):
    r'\'.*\''
    t.value = t.value[1:-1]
    return t

def t_REGEXP(t):
    r'[Rr][Ee][Gg][Ee][Xx][Pp]'
    t.value = REGEXP_
    return t

def t_NEQUAL(t):
    r'<>|!='
    t.value = NEQUAL_
    return t

def t_EQUAL(t):
    r'==?'
    t.value = EQUAL_
    return t

# /music/not hip hop, /music/!hip hop, /music/not attr#bitrate
def t_NEGATION(t):
    r'[Nn][Oo][Tt]|!'
    t.value = NEGATION_
    return t

def t_DATE(t):
    r'\d{4}-\d{2}-\d{2}'
    t.value = datatypes.generic.DateType.cast(t.value)
    return t

def t_TIME(t):
    r'[0-2]?[0-9]:[0-5][0-9](:[0-6][0-9])?'
    t.value = datatypes.generic.TimeType.cast(t.value)
    return t

def t_REAL(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print "Float value too large", t.value
        t.value = 0.0
    return t


def t_INTEGER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Integer value too large", t.value
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    t.lexer.skip(1)
    raise VHFSException("Lexer Exception (%s)" % `t`, err_code = 0)
    
# Build the lexer
import ply.lex as lex
lex.lex()

result = None

def p_subpath(t):
    '''subpath : subpath path_part
               | path_part
    '''
    if len(t) == 3:
        t[0] = PathNode(t[1]) + PathNode(t[2])
    elif len(t) == 2:
        t[0] = PathNode(t[1])

def p_path_part(t):
    '''path_part : DELIMITER path_part_node
                 | DELIMITER'''
    if len(t) == 2:
        t[0] = PathNode([])
    else:
        t[0] = t[2]

def p_path_part_node(t):
    '''
        path_part_node : path_node
                       | type_casted_node
    '''
    t[0] = t[1]

def p_type_casted_node(t):
    '''
        type_casted_node : cast_part_node path_node
    '''
    t[1].value = t[2]
    t[2].parent = t[1]
    t[0] = t[1]

def p_path_node(t):
    '''path_node : file_node
                    | tag_node
                    | attr_node
                    | ambigous_node
	'''
    t[0] = t[1]

# for /some_id: we must dynamically determine wether some_id is a tag or an
# attribute
# /tag#some_id:
# 
def p_ambigous_node(t):
    '''
    ambigous_node : NEGATION identifier
                  | identifier func_node 
    '''
    
    if t[1] == NEGATION_:
        f_node = FuncNode(name = NEGATION_)
        t[0] = AmbigousNode(name = t[2], func_node = f_node)
    else:
        f_node = t[2]
        t[0] = AmbigousNode(name = t[1], func_node = f_node)

    f_node.parent = t[0]


def p_tag_node(t):
    '''tag_node : identifier
    '''
    t[0] = TagNode(name = t[1])

def p_attr_node(t):
    '''attr_node : identifier EQUAL func_arg
                    | identifier NEQUAL func_arg
                    | identifier LT func_arg
                    | identifier LE func_arg
                    | identifier GT func_arg
                    | identifier GE func_arg
                    | identifier ASSIGN func_arg
                    | identifier LIKE STRING
                    | identifier REGEXP STRING
                    '''
    mapping = {
        '>'      : 'gt',
        '>='     : 'ge',
        '<'      : 'lt',
        '<='     : 'le',
        ':='     : 'weq', # weak equal - if attribute didn't exists ignore condition
        EQUAL_   : 'eq',
        NEQUAL_  : 'neq',
        LIKE_    : 'like',
        REGEXP_  : 'regexp'
    }
    func = FuncNode(name = mapping[t[2]], args = [t[3]])
    t[0] = AttributeNode(name = t[1], func_node = func)
    func.parent = t[0]

def p_type_casted_value(t):
    '''type_casted_value : cast_part_node func_arg 
    '''
    t[1].value = t[2]
    t[0] = t[1]

def p_cast_part_node(t):
    '''cast_part_node : LPAREN TYPE_CAST RPAREN 
                      | LPAREN TYPE_CAST func_node RPAREN 
    '''
    if len(t) == 4:
        t[0] = TypeCastNode(type = t[2])
    elif len(t) == 5:
        t[0] = TypeCastNode(type = t[2], func_node = t[3])
        t[3].parent = t[0]

def p_file_node(t):
    '''file_node : FILE 
                 | FILE func_node'''
    if len(t) == 2:
        t[0] = FileNode(name = t[1])
    elif len(t) == 3:
        t[0] = FileNode(name = t[1], func_node = t[2])
        t[2].parent = t[0]

# /music/album:like %usic (:like %usic)
# /music/album:regexp m?sic (:regexp m?sic)
# /music/:limit 10
def p_func_node(t):
    '''func_node : FUNC ARG_SPECIFIER args
                 | FUNC
    '''
    if t[1] == RAW_FUNC_SPECIFIER:
        t[1] = UNSPECIFIED_SYM
    else:
        t[1] = t[1][1:]
    if len(t) == 4:
        # FIXME: args must have only Node instances
        t[0] = FuncNode(name = t[1], args = t[3])
    else:
        t[0] = FuncNode(name = t[1], args = [])

def p_date_time(t):
    '''date_time : DATE ARG_SPECIFIER TIME
                 | DATE ARG_SPECIFIER INTEGER
    '''
    if not hasattr(t[3], 'hour'):
        t[3] = datatypes.generic.TimeType.cast(str(t[3]))
    t[0] = datetime.datetime(t[1].year, t[1].month, t[1].day, \
                             t[3].hour, t[3].minute, t[3].second)

# examples of usage arg list: 
# :limit 10
# :order name, album, bitrate
def p_args(t):
    '''args : args ARG_SEPARATOR func_arg 
            | func_arg'''
    t[0] = []
    if len(t) == 4:
        t[1].append(t[3])
        t[0].extend(t[1])
    else:
        t[0].append(t[1])
        
def p_func_arg(t):
    '''func_arg : identifier
                | INTEGER
                | REAL
                | STRING
                | DATE
                | TIME
                | type_casted_value
                | date_time
                '''
    t[0] = t[1]

def p_identifier(t):
    '''identifier : ID'''
    t[0] = t[1][1:]

def p_error(t):
    if t != None:
        raise VHFSException("Syntax Error Exception (%s)" % `t`, err_code = 0)

import ply.yacc as yacc
yacc.yacc()
