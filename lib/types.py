class BeaverException(Exception):
    pass
            

class Uri(object):
    def __init__(self, url):
        self.url = str(url)
    def __str__(self): return '<%s>' % self.url
    def __repr__(self): return str(self)
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
    def __repr__(self): return str(self)
    def apply_prefixes(self, prefixes): pass
    
    
class Variable(object):
    def __init__(self, *ident):
        self.ident = ident
    def __str__(self): return '?%s' % self.ident
    def __repr__(self): return str(self)
    def __eq__(self, x): return str(self) == str(x)
    def __hash__(self): return hash(str(self))
        
        
class Pattern(object):
    def __init__(self, *vars):
        self.vars = vars
    def __str__(self): return (' ' if self.vars else '') + ' '.join([str(var) for var in self.vars])
    def __repr__(self): return str(self)
    
EmptyPattern = Pattern(*[])
