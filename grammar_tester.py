import parser
import nodes

while 1:
    try:
        s = raw_input('vhfs > ')
    except EOFError:
        break
    out = parser.yacc.parse(s)
    print str(out)
