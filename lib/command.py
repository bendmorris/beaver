from types import BeaverException, Variable
import urllib2


class Command:
    def execute(self, graph):
        raise BeaverException('This command has not yet been implemented.')
    def __repr__(self): return '%s(**%s)' % (str(self.__class__).split('.')[-1], self.__dict__)
        
class PrefixCommand(Command):
    def __init__(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
    def execute(self, graph):
        graph.prefix_to_uri[self.prefix] = self.uri    
        
class DefCommand(Command):
    def __init__(self, ident, pattern, *triples):
        self.ident = ident
        self.pattern = pattern
        self.triples = triples
    def execute(self, graph):
        ident = str(self.ident)
        if not ident in graph.defs: graph.defs[ident] = []
        graph.defs[ident] = [(self.pattern, self.triples)] + graph.defs[ident]
        
class CallCommand(Command):
    def __init__(self, ident, pattern):
        self.ident = ident
        self.pattern = pattern
    def execute(self, graph):
        try: patterns = graph.defs[str(self.ident)]
        except KeyError: raise BeaverException('Undefined variable: %s' % self.ident)
        
        match = False
        for (pattern, stmts) in patterns:
            if len(pattern.vars) != len(self.pattern.vars):
                continue
            else:
                match = True
                for given, to_match in zip(self.pattern.vars, pattern.vars):
                    if not isinstance(to_match, Variable):
                        match = given == to_match
                    if not match: break
                        
                    
            if match:
                graph.execute(stmts, context={str(to_match): given 
                                              for given, to_match
                                              in zip(self.pattern.vars, pattern.vars)})
                return
                
        raise BeaverException('No pattern matched: %s %s' % (self.ident, self.pattern))
        
class ImportCommand(Command):
    def __init__(self, uri):
        self.uri = uri
    def execute(self, graph):
        stream = urllib2.urlopen(str(self.uri))
        graph.parse(stream=stream)
