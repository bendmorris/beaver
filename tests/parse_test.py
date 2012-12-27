from beaver.lib.types import *
from beaver.lib.graph import *
from beaver.lib.command import *
from beaver.lib.parser import *
import doctest

def test():
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
    '''

doctest.testmod()
