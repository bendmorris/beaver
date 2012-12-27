from lib.types import *
from lib.graph import *
from lib.command import *
from lib.parser import *
import doctest


def parser_test():
    '''
    >>> str(variable.parseString('?a', parseAll=True)[0])
    '?a'
    >>> literal.parseString('1.0', parseAll=True)[0]
    1.0
    >>> literal.parseString('1', parseAll=True)[0]
    1
    >>> str(expression.parseString('1 2 3 .', parseAll=True)[0])
    '1 2 3'
    >>> str(expression.parseString('?a <http://www.example.com> abc:def .', parseAll=True)[0])
    '?a <http://www.example.com> abc:def'
    >>> [str(s) for s in (expression.parseString('<a> a <b> ; <c> <d>, <e> .', parseAll=True))]
    ['<a> rdf:type <b>', '; <c> <d>, <e>']
    >>> expression.parseString('@reinit', parseAll=True)[0]
    @reinit
    >>> expression.parseString('@draw <test.png>', parseAll=True)[0]
    @draw <test.png>
    >>> expression.parseString('@import <test.ttl>', parseAll=True)[0]
    ImportCommand'>(**{'uri': Uri('test.ttl')})
    >>> expression.parseString('@load <test.xml>', parseAll=True)[0]
    LoadCommand'>(**{'uri': Uri('test.xml')})
    >>> expression.parseString('?a = 1 2 3 .', parseAll=True)[0]
    DefCommand'>(**{'pattern': Pattern(([],)), 'ident': Variable(('a',)), 'triples': (Statement(1, 2, 3, ()),)})
    '''

def graph_test():
    '''
    >>> g = Graph()
    >>> g.execute(Statement(Uri('node1'), QUri('p','node2'), Uri('node3'), Uri('node4')))
    >>> g.statements
    {Uri('node1'): {QUri('p', 'node2'): set([Uri('node3'), Uri('node4')])}}
    '''

doctest.testmod()
