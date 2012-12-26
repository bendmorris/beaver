from cStringIO import StringIO
from pyparsing import *
ParserElement.enablePackrat()
from types import *
from command import *


# expressions
url = Word(alphanums + "0123456789-._~:/?#[]@!$&'()*+,;=")
ident = Word(alphanums + "_")
uri = (
       (Suppress("<") + url + Suppress(">")).setParseAction(lambda x: Uri(*x)) | 
       (ident + Suppress(":") + ident).setParseAction(lambda x: QUri(*x)) | 
       (Suppress("a").setParseAction(lambda x: QUri('rdf', 'type')))
       )
comment = pythonStyleComment.suppress()
literalString = (sglQuotedString | dblQuotedString)
integer = Word(nums)
real = ( Combine(Word(nums) + Optional("." + Word(nums))
                 + oneOf("E e") + Optional( oneOf('+ -')) + Word(nums))
         | Combine(Word(nums) + "." + Word(nums))
         )
literalNumber = integer.setParseAction(lambda x: int(*x)) | real.setParseAction(lambda x: float(*x))
literal = literalString | literalNumber

variable = (Suppress('?') + Optional(ident, default='')).setParseAction(lambda x: Variable(*x))
triplet = (uri | literal | variable).setParseAction(lambda x: x[0])
pattern = OneOrMore(triplet)
pattern.setParseAction(lambda x: Pattern(*x))

triple = (triplet + triplet + triplet).setParseAction(lambda x: Stmt(*x))
continued_triple = (';' + triplet + triplet).setParseAction(lambda x: Stmt(*x))
triples = Forward()
triples << (
            (triple + Suppress('.')) | 
            (triple + OneOrMore(continued_triple) + Suppress('.')) | 
            (Suppress('{') + OneOrMore(triples) + Suppress('}'))
            )
            
# commands
prefix_cmd = (Suppress('@prefix') + ident + Suppress(":") + uri).setParseAction(lambda x: PrefixCommand(*x))
load_cmd = (Suppress('@load') + uri).setParseAction(lambda x: LoadCommand(*x))
import_cmd = (Suppress('@import') + uri).setParseAction(lambda x: ImportCommand(*x))
definition_cmd = (variable + Optional(pattern, default=Pattern([])) + Suppress('=') + triples).setParseAction(lambda x: DefCommand(*x))
call_cmd = (variable + Optional(pattern, default=Pattern([]))).setParseAction(lambda x: CallCommand(*x))
command = (
           prefix_cmd | 
           load_cmd | 
           import_cmd | 
           definition_cmd |
           call_cmd
           ) + Optional(".").suppress()
           
expression = (comment | triples | command)


def parse_string(string):
    with StringIO(treetext) as handle:
        return parse_stream(handle)

def parse_file(filename):
    with open(filename, 'r') as handle:
        return parse_stream(handle)

def parse_stream(handle):
    # TODO: add a lazy scanFile method to pyparsing.py so that the whole handle 
    #       doesn't need to be read at once
    text = handle.read()
    return expression.scanString(text)
