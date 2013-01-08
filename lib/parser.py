from cStringIO import StringIO
from pyparsing import *
ParserElement.enablePackrat()
from types import *
from statement import Statement
from command import *


# Turtle BNF: http://www.w3.org/TeamSubmission/turtle/#sec-grammar-grammar

expression = Forward()

comment = pythonStyleComment.suppress()
relativeURI = Word(alphanums + "-._~:/?#[]@!$&'()*+,;=")
name = Word(alphanums + "_")
prefixName = name
language = Word(alphas, alphanums + '-')
uriref = Suppress('<') + relativeURI + Suppress('>')
uriref.setParseAction(lambda x: Uri(*x))
qname = Optional(prefixName, default='') + Suppress(':') + Optional(name, default='')
qname.setParseAction(lambda x: QUri(*x))
nodeID = Suppress('_:') + name
nodeID.setParseAction(lambda x: QUri('_', x[0]))
variable = (Suppress('?') + Optional(name, default=''))
variable.setParseAction(lambda x: Variable(*x))
resource = uriref | qname | variable
resource.setParseAction(lambda x: x[0])
integer = Word(nums)
integer.setParseAction(lambda x: Value(int(''.join(x))))
double = (Combine(Word(nums) + Optional("." + Word(nums))
                  + oneOf("E e") + Optional( oneOf('+ -')) + Word(nums))
          | Combine(Word(nums) + "." + Word(nums))
          )
double.setParseAction(lambda x: Value(float(''.join(x))))
bool_true = Suppress('true')
bool_true.setParseAction(lambda x: Value(True))
bool_false = Suppress('false')
bool_false.setParseAction(lambda x: Value(False))
boolean = bool_true | bool_false
longString = Regex(r'''("{3}([\s\S]*?"{3}))|('{3}([\s\S]*?'{3}))''')
str_literal = longString | quotedString
str_literal.setParseAction(lambda x: Value(''.join(x)))
datatypeString = str_literal + Suppress('^^') + Suppress(resource)
literal = datatypeString | (str_literal + Optional(Suppress('@') + language)) | double | integer | boolean
predicateObjectList = Forward()
collection = Forward()
blank = nodeID | Suppress('[]') | (Suppress('[') + predicateObjectList + Suppress(']')) | collection
blank.setParseAction(lambda x: x[0])
object = variable | resource | blank | literal
predicate = resource
verb = variable | predicate | (Suppress('a').setParseAction(lambda x: QUri('rdf', 'type')))
itemList = OneOrMore(object | verb)
collection << Suppress('(') + Optional(itemList) + Suppress(')')
collection.setParseAction(lambda x: Collection(*x))
pattern = collection | Optional(itemList).setParseAction(lambda x: Collection(*x))
subject = variable | resource | blank
subject.setParseAction(lambda x: x[0])
verb.setParseAction(lambda x: x[0])
objectList = delimitedList(object)
objectList.setParseAction(lambda x: tuple(x))
verbObjectList = verb + objectList
verbObjectList.setParseAction(lambda x: (x[0], tuple(x[1])))
predicateObjectList << (verbObjectList + ZeroOrMore(Suppress(';') + verbObjectList))
triples = subject + predicateObjectList
triples.setParseAction(lambda x: Statement(x[0], x[1:]))
base = Suppress('@base') + uriref
base.setParseAction(lambda x: BaseCommand(*x))
prefixID = Suppress('@prefix') + Optional(prefixName, default='') + Suppress(':') + uriref
prefixID.setParseAction(lambda x: PrefixCommand(*x))
directive = prefixID | base
statement = (directive | triples | comment) + Optional('.').suppress()

            
# commands
for_cmd = (Suppress('@for') + variable + Suppress('in') + collection + expression)
for_cmd.setParseAction(lambda x: ForCommand(*x))
load_cmd = (Suppress('@load') + uriref)
load_cmd.setParseAction(lambda x: LoadCommand(*x))
import_cmd = (Suppress('@import') + uriref)
import_cmd.setParseAction(lambda x: ImportCommand(*x))
del_cmd = (Suppress('@del') + expression)
del_cmd.setParseAction(lambda x: DelCommand(*x))
draw_cmd = (Suppress('@draw') + uriref)
draw_cmd.setParseAction(lambda x: DrawCommand(*x))
write_cmd = (Suppress('@out') + Optional(uriref))
write_cmd.setParseAction(lambda x: OutCommand(*x))
reinit_cmd = (Suppress('@reinit'))
reinit_cmd.setParseAction(lambda x: ReinitCommand())
f_definition = (variable + pattern + Suppress('=') + expression)
f_definition.setParseAction(lambda x: DefCommand(*x))
v_definition = (variable + Literal('=').setParseAction(lambda x: None) + object)
v_definition.setParseAction(lambda x: DefCommand(*x))
definition = f_definition | v_definition
function_call = (variable + pattern)
function_call.setParseAction(lambda x: FuncCall(*x))
command = (
           definition |
           function_call |
           for_cmd |
           load_cmd | 
           import_cmd | 
           del_cmd |
           draw_cmd |
           write_cmd |
           reinit_cmd
           ) + Optional(".").suppress()
           
expression << ((Suppress('{') + OneOrMore(expression) + Suppress('}')) |
               (command | statement)
                ) + Optional('.').suppress()
                
document = ZeroOrMore(expression)


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
    return document.parseString(text, parseAll=True)
