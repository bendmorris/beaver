import collections


class BeaverException(Exception):
    pass

class Statement(object):
    '''A triple statement.'''
    def __init__(self, subj, verb, obj, *other_objs):
        self.subj = subj
        self.verb = verb
        self.obj = obj
        self.other_objs = other_objs
    def __str__(self): return '%s %s %s' % (self.subj, self.verb, ', '.join([str(self.obj)] + [str(o) for o in self.other_objs]))
    def __repr__(self): return 'Statement(%s, %s, %s, %s)' % (repr(self.subj), repr(self.verb), repr(self.obj), '(%s)' % ','.join([repr(r) for f in self.other_objs]))

Stmt = Statement

        
class Uri(object):
    def __init__(self, url):
        self.url = str(url)
    def __str__(self): return '<%s>' % self.url
    def __repr__(self): return 'Uri(%s)' % repr(str(self.url))
    def __add__(self, x): return Uri(str(self) + str(x))
    def __eq__(self, x): return str(self) == str(x)
    def __hash__(self): return hash(str(self))
    
    def apply_prefix(self, prefixes):
        this_uri = str(self)[1:-1]
        # try to apply prefixes, by the length of their respective URIs
        for prefix, uri in sorted(prefixes.items(), key=lambda l: len(str(l[1])), reverse=True):
            match_uri = str(uri)[1:-1]
            if this_uri.startswith(match_uri) and len(this_uri) > len(match_uri):
                return QUri(prefix, this_uri.replace(match_uri, '', 1))
        return self

class QUri(Uri):
    def __init__(self, prefix, url=None):
        if url is None:
            prefix, url = prefix.split(':')
        self.prefix = str(prefix)
        self.url = str(url)
    def __str__(self): return '%s:%s' % (self.prefix, self.url)
    def __repr__(self): return 'QUri(%s, %s)' % (repr(str(self.prefix)), repr(str(self.url)))
    def apply_prefixes(self, prefixes): pass
    
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
