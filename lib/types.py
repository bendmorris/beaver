class BeaverException(Exception):
    def __init__(self, s):
        Exception.__init__(self, 'ERROR: %s' % s)
            

class Uri(object):
    def __init__(self, url):
        self.url = str(url)
    def __str__(self): return '<%s>' % self.url
    def __repr__(self): return str(self)
    def __add__(self, x): return Uri(str(self) + str(x))
    def __eq__(self, x): return str(self) == str(x)
    def __hash__(self): return hash(str(self))
    
    def apply_prefix(self, graph):
        this_uri = self.resolve(graph)
        prefixes = graph.prefixes
        # try to apply prefixes, by the length of their respective URIs
        for prefix, uri in sorted(prefixes.items(), key=lambda l: len(str(l[1])), reverse=True):
            match_uri = str(uri)[1:-1]
            if this_uri.startswith(match_uri) and len(this_uri) > len(match_uri):
                return QUri(prefix, this_uri.replace(match_uri, '', 1))
        return self

    def resolve(self, graph):
        return str(self)[1:-1]


class QUri(Uri):
    def __init__(self, prefix, url=None):
        if url is None:
            prefix, url = prefix.split(':')
        self.prefix = str(prefix)
        self.url = str(url)
    def __str__(self): return '%s:%s' % (self.prefix, self.url)
    def __repr__(self): return str(self)
    def apply_prefix(self, graph): return self
    
    
class Variable(object):
    def __init__(self, *ident):
        self.ident = ident
    def __str__(self): return '?%s' % (self.ident)
    def __repr__(self): return str(self)
    def __eq__(self, x): return str(self) == str(x)
    def __hash__(self): return hash(str(self))
    
    
class Value(object):
    def __init__(self, value):
        self.value = value
    def __str__(self): 
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)
    def __repr__(self): return str(self)
    def __eq__(self, x): return self.value == x
    def __hash__(self): return hash(self.value)
    def apply_prefix(self, graph): return self
        
        
class Collection(object):
    def __init__(self, *vars):
        self.vars = vars
    def __str__(self): return '( ' + ' '.join([str(var) for var in self.vars]) + ' )'
    def __repr__(self): return str(self)
    def __eq__(self, x): return self.vars == x.vars
    
EmptyCollection = Collection()


def updated_context(context, new_context):
    if not new_context: return context
    context = context.copy()
    
    for (key, value) in new_context.items():
        if not key in context: context[key] = []
        context[key] = value + context[key]
        
    return context
