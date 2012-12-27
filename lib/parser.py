from cStringIO import StringIO
from pyparsing import *
ParserElement.enablePackrat()
from types import *
from command import *


# expressions
expression = Forward()

url = Word(alphanums + "-._~:/?#[]@!$&'()*+,;=")
ident = Word(alphanums + "_")
wildcard = Literal('*')
wildcard.setParseAction(lambda x: Uri(*x))
rdftype = Suppress("a")
rdftype.setParseAction(lambda x: QUri('rdf', 'type'))

full_uri = (Suppress("<") + url + Suppress(">"))
full_uri.setParseAction(lambda x: Uri(*x))
quri = (ident + Suppress(":") + ident)
quri.setParseAction(lambda x: QUri(*x))
uri = full_uri | quri

comment = pythonStyleComment.suppress()
literalString = (sglQuotedString | dblQuotedString)
integer = Word(nums)
integer.setParseAction(lambda x: int(''.join(x)))
real = ( Combine(Word(nums) + Optional("." + Word(nums))
                 + oneOf("E e") + Optional( oneOf('+ -')) + Word(nums))
         | Combine(Word(nums) + "." + Word(nums))
         )
real.setParseAction(lambda x: float(''.join(x)))
literalNumber = real | integer
literal = literalString | literalNumber

variable = (Suppress('?') + Optional(ident, default=''))
variable.setParseAction(lambda x: Variable(*x))
triplet = (variable | uri | literal)
triplet.setParseAction(lambda x: x[0])
pattern = OneOrMore(triplet)
pattern.setParseAction(lambda x: Pattern(*x))

subj = triplet
verb = wildcard | triplet | rdftype
obj = wildcard | triplet
triple = (subj + verb + obj + Optional(OneOrMore(Suppress(',') + obj)))
triple.setParseAction(lambda x: Stmt(*x))
continued_triple = (';' + verb + obj + Optional(OneOrMore(Suppress(',') + obj)))
continued_triple.setParseAction(lambda x: Stmt(*x))
triples = (
           (triple + OneOrMore(continued_triple)) | triple 
           )
            
# commands
prefix_cmd = (Suppress('@prefix') + ident + Suppress(":") + uri).setParseAction(lambda x: PrefixCommand(*x))
load_cmd = (Suppress('@load') + uri).setParseAction(lambda x: LoadCommand(*x))
import_cmd = (Suppress('@import') + uri).setParseAction(lambda x: ImportCommand(*x))
del_cmd = (Suppress('@del') + expression).setParseAction(lambda x: DelCommand(*x))
draw_cmd = (Suppress('@draw') + uri).setParseAction(lambda x: DrawCommand(*x))
reinit_cmd = (Suppress('@reinit')).setParseAction(lambda x: ReinitCommand())
function_def = (variable + pattern + Suppress('=') + expression)
function_def.setParseAction(lambda x: DefCommand(*x))
var_def = (variable + Suppress('=') + (expression | triplet))
var_def.setParseAction(lambda x: DefCommand(x[0], Pattern([]), *x[1:]))
definition_cmd = (function_def | var_def)
call_cmd = (variable + Optional(pattern, default=Pattern([])))
call_cmd.setParseAction(lambda x: CallCommand(*x))
command = (
           prefix_cmd | 
           load_cmd | 
           import_cmd | 
           del_cmd |
           draw_cmd |
           reinit_cmd
           ) + Optional(".").suppress()
           
expression << ((Suppress('{') + OneOrMore(expression) + Suppress('}')) |
               ((comment | definition_cmd | call_cmd | triples | command))
                ) + Optional('.').suppress()


def parse_string(string):
    handle = StringIO(string)
    return parse_stream(handle)

def parse_file(filename):
    with open(filename, 'r') as handle:
        return parse_stream(handle)

def parse_stream(handle):
    # TODO: add a lazy scanFile method to pyparsing.py so that the whole handle 
    #       doesn't need to be read at once
    text = handle.read()
    return expression.scanString(text)