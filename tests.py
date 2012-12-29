from lib.types import *
from lib.graph import *
from lib.command import *
from lib.parser import *
import os
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
    ImportCommand(**{'uri': Uri('test.ttl')})
    >>> expression.parseString('@load <test.xml>', parseAll=True)[0]
    LoadCommand(**{'uri': Uri('test.xml')})
    >>> expression.parseString('?a = 1 2 3 .', parseAll=True)[0]
    DefCommand(**{'pattern': Pattern(()), 'ident': Variable(('a',)), 'triples': (Statement(1, 2, 3),)})
    >>> expression.parseString('@prefix ex: <http://www.example.com/example#>', parseAll=True)[0]
    PrefixCommand(**{'prefix': 'ex', 'uri': Uri('http://www.example.com/example#')})
    >>> expression.parseString('@for @a in 1 2 3 4 5 { @a <b> <c> . }')
    '''

def graph_test():
    '''
    >>> g = Graph()
    >>> g.execute(Statement(Uri('node1'), QUri('p','node2'), Uri('node3'), Uri('node4')))
    >>> g.statements
    {Uri('node1'): {QUri('p', 'node2'): set([Uri('node3'), Uri('node4')])}}
    >>> prefix = PrefixCommand(prefix='ex', uri=Uri('http://www.example.com/example#'))
    >>> g.execute(prefix)
    >>> g.prefixes
    {'bvr': Uri('http://www.beaver-lang.org/1/0/0/syntax#'), 'rdf': Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'ex': Uri('http://www.example.com/example#')}
    >>> str(Uri('http://www.example.com/example#sample').apply_prefix(g.prefixes))
    'ex:sample'
    >>> try: os.remove('test.png')
    ... except OSError: pass
    >>> os.path.exists('test.png')
    False
    >>> g.draw('test.png')
    >>> os.path.exists('test.png')
    True
    >>> g.parse(text='@load <test.xml>')
    1
    >>> g.parse(text='@import <test.bvr>')
    1
    >>> g.parse(text='@reinit')
    1
    >>> g.parse(text='@load <http://www.nexml.org/nexml/examples/trees.rdf>')
    1
    >>> sorted([str(s) for s in g.statements.keys()])[:5]
    ['<http://example.org/e1>', '<http://example.org/e2>', '<http://example.org/e3>', '<http://example.org/e4>', '<http://example.org/e5>']
    '''

doctest.testmod()
