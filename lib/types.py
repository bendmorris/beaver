import collections


class BeaverException(Exception):
    pass

class Statement(object):
    '''A triple statement.'''
    def __init__(self, subj, verb, *obj):
        self.subj = subj
        self.verb = verb
        self.obj = obj
    def __str__(self): return '%s %s %s' % (self.subj, self.verb, ', '.join([str(o) for o in self.obj]))
    def __repr__(self): return 'Statement(%s, %s, %s)' % (repr(self.subj), repr(self.verb), repr(self.obj))

Stmt = Statement

        
class Uri(object):
    def __init__(self, url):
        self.url = str(url)
        
    def __str__(self): return '<%s>' % self.url
    def __repr__(self): return 'Uri(%s)' % repr(str(self.url))
    def __add__(self, x): return Uri(str(self) + str(x))
    def __eq__(self, x): return str(self) == str(x)

class QUri(Uri):
    def __init__(self, prefix, url=None):
        if url is None:
            prefix, url = prefix.split(':')
        self.prefix = str(prefix)
        self.url = str(url)
    def __str__(self): return '%s:%s' % (self.prefix, self.url)
    def __repr__(self): return 'QUri(%s, %s)' % (repr(str(self.prefix)), repr(str(self.url)))
    
class Variable(object):
    def __init__(self, ident):
        self.ident = ident
    def __str__(self): return '?%s' % self.ident
    def __repr__(self): return 'Variable(%s)' % repr(self.ident)
    def __eq__(self, x): return str(self) == str(x)
        
class Pattern(object):
    def __init__(self, *vars):
        self.vars = vars
    def __str__(self): return ' '.join([str(var) for var in self.vars])
    def __repr__(self): return 'Pattern(%s)' % repr(self.vars)
