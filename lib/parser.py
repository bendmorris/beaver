from cStringIO import StringIO
from pyparsing import *
ParserElement.enablePackrat()
from types import *
from statement import Statement
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
literalString.setParseAction(lambda x: Value(''.join(x)))
integer = Word(nums)
integer.setParseAction(lambda x: Value(int(''.join(x))))
real = ( Combine(Word(nums) + Optional("." + Word(nums))
                 + oneOf("E e") + Optional( oneOf('+ -')) + Word(nums))
         | Combine(Word(nums) + "." + Word(nums))
         )
real.setParseAction(lambda x: Value(float(''.join(x))))
literalNumber = real | integer
literalTrue = Suppress('true')
literalTrue.setParseAction(lambda x: Value(True))
literalFalse = Suppress('false')
literalFalse.setParseAction(lambda x: Value(False))
literalBool = literalTrue | literalFalse
literal = literalBool | literalString | literalNumber

variable = (Suppress('?') + Optional(ident, default=''))
variable.setParseAction(lambda x: Variable(*x))
triplet = (variable | uri | literal | rdftype)
triplet.setParseAction(lambda x: x[0])
# TODO: optional parentheses
pattern = OneOrMore(triplet)
pattern.setParseAction(lambda x: Pattern(*x))

triple = (triplet + triplet + triplet + Optional(OneOrMore(Suppress(',') + triplet)))
triple.setParseAction(lambda x: Statement(*x))
continued_triple = (';' + triplet + triplet + Optional(OneOrMore(Suppress(',') + triplet)))
continued_triple.setParseAction(lambda x: Statement(*x))
generic_stmt = OneOrMore(Optional(Suppress(',')) + triplet)
generic_stmt.setParseAction(lambda x: Statement(*x))
statements = (
              (triple + OneOrMore(continued_triple)) | generic_stmt
              )
            
# commands
for_cmd = (Suppress('@for') + variable + Suppress('in') + Suppress('(') + pattern + Suppress(')') + expression)
for_cmd.setParseAction(lambda x: ForCommand(*x))
prefix_cmd = (Suppress('@prefix') + ident + Suppress(":") + uri)
prefix_cmd.setParseAction(lambda x: PrefixCommand(*x))
base_cmd = (Suppress('@base') + uri)
base_cmd.setParseAction(lambda x: BaseCommand(*x))
load_cmd = (Suppress('@load') + uri)
load_cmd.setParseAction(lambda x: LoadCommand(*x))
import_cmd = (Suppress('@import') + uri)
import_cmd.setParseAction(lambda x: ImportCommand(*x))
del_cmd = (Suppress('@del') + expression)
del_cmd.setParseAction(lambda x: DelCommand(*x))
draw_cmd = (Suppress('@draw') + uri)
draw_cmd.setParseAction(lambda x: DrawCommand(*x))
write_cmd = (Suppress('@out') + Optional(uri))
write_cmd.setParseAction(lambda x: OutCommand(*x))
reinit_cmd = (Suppress('@reinit'))
reinit_cmd.setParseAction(lambda x: ReinitCommand())
function_def = (variable + pattern + Suppress('=') + expression)
function_def.setParseAction(lambda x: DefCommand(*x))
var_def = (variable + Suppress('=') + expression)
var_def.setParseAction(lambda x: DefCommand(x[0], EmptyPattern, *x[1:]))
definition_cmd = (function_def | var_def)
command = (
           for_cmd |
           prefix_cmd | 
           base_cmd | 
           load_cmd | 
           import_cmd | 
           del_cmd |
           draw_cmd |
           write_cmd |
           reinit_cmd
           ) + Optional(".").suppress()
           
expression << ((Suppress('{') + OneOrMore(expression) + Suppress('}')) |
               ((comment | definition_cmd | statements | command))
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
