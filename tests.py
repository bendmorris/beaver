from lib.types import *
from lib.graph import *
from lib.command import *
from lib.parser import *
import os
import doctest
import sys


if len(sys.argv) > 1:
    verbose = eval(sys.argv[1])
else: verbose=False


def parser_tests():
    '''
    >>> variable.parseString('?a', parseAll=True)[0]
    ?a
    >>> literal.parseString('1.0', parseAll=True)[0]
    1.0
    >>> literal.parseString('1', parseAll=True)[0]
    1
    >>> literal.parseString('"abc"', parseAll=True)[0]
    "abc"
    >>> expression.parseString('1 2 3 .', parseAll=True)[0]
    1 2 3
    >>> expression.parseString('?a <http://www.example.com> abc:def .', parseAll=True)[0]
    ?a <http://www.example.com> abc:def
    >>> [s for s in expression.parseString('<a> a <b> ; <c> <d>, <e> .', parseAll=True)]
    [<a> rdf:type <b>, ; <c> <d>, <e>]
    >>> expression.parseString('@reinit', parseAll=True)[0]
    @reinit
    >>> expression.parseString('@draw <test.png>', parseAll=True)[0]
    @draw <test.png>
    >>> expression.parseString('@import <test.ttl>', parseAll=True)[0]
    @import <test.ttl>
    >>> expression.parseString('@load <test.xml>', parseAll=True)[0]
    @load <test.xml>
    >>> expression.parseString('?a = 1 2 3 .', parseAll=True)[0]
    ?a = { 1 2 3 }
    >>> expression.parseString('@prefix ex: <http://www.example.com/example#>', parseAll=True)[0]
    @prefix ex: <http://www.example.com/example#>
    >>> expression.parseString('@for ?a in (1 <a> ?x b:c "five") { ?a <b> <c> . }', parseAll=True)[0]
    @for ?a in ( 1 <a> ?x b:c "five" ) ?a <b> <c>
    >>> expression.parseString('@out', parseAll=True)[0]
    @out
    >>> expression.parseString('@out <test.ttl>', parseAll=True)[0]
    @out <test.ttl>
    >>> expression.parseString('@reinit', parseAll=True)[0]
    @reinit
    '''


def graph_tests():
    '''
    >>> g = Graph()
    >>> g.execute(Statement(Uri('node1'), QUri('p','node2'), Uri('node3'), Uri('node4')))
    >>> g.statements
    {<node1>: {p:node2: set([<node3>, <node4>])}}
    >>> prefix = PrefixCommand(prefix='ex', uri=Uri('http://www.example.com/example#'))
    >>> g.execute(prefix)
    >>> g.prefixes
    {'rdf': <http://www.w3.org/1999/02/22-rdf-syntax-ns#>, 'ex': <http://www.example.com/example#>}
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
    >>> g.parse(text='<a> a <b>, <c> .')
    1
    >>> g.reinit()
    >>> g.parse(text='@load <http://www.nexml.org/nexml/examples/trees.rdf>')
    1
    >>> sorted([str(s) for s in g.statements.keys()])[:5]
    ['<http://example.org/e1>', '<http://example.org/e2>', '<http://example.org/e3>', '<http://example.org/e4>', '<http://example.org/e5>']
    >>> g.reinit()
    >>> g.parse(text='@for ?x in (1 2 3 4 5) { <a> <b> ?x . }')
    1
    >>> g.statements[Uri('a')][Uri('b')]
    set([1, 2, 3, 4, 5])
    >>> g.parse(text="?cat ?name = { ?name a example:cat . <ben> <has_cat> ?name . }")
    1
    >>> g.parse(text="@for ?name in ('whiskers' 'socks' 'oreo') ?cat ?name .")
    1
    >>> g.statements[Uri('ben')][Uri('has_cat')]
    set(['whiskers', 'socks', 'oreo'])
    >>> g.reinit()
    >>> g.parse(text='?a ?b = { <things> <not_a_one> ?b } . ?a 1 = { <things> <is_a_one> 1 } .')
    2
    >>> g.parse(text='@for ?x in (1 2 <bob> "1") ?a ?x .')
    1
    >>> g.statements[Uri('things')][Uri('is_a_one')]
    set([1])
    >>> g.statements[Uri('things')][Uri('not_a_one')]
    set(["1", 2, <bob>])
    >>> g.parse(text='@for ?x in (2 <bob> "1") @del <things> <not_a_one> ?x . @del <things> <is_a_one> 1 .')
    2
    >>> g.statements
    {}
    '''


doctest.testmod(verbose=verbose)
