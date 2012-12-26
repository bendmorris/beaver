from types import BeaverException, Variable, Uri, Statement
import urllib2


class Command:
    def execute(self, graph):
        raise BeaverException('This command (%s) has not yet been implemented.' % self.__doc__)
    def __repr__(self): return '%s(**%s)' % (str(self.__class__).split('.')[-1], self.__dict__)
        
class PrefixCommand(Command):
    '''Define a URI prefix.'''
    def __init__(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
    def __str__(self): return '@prefix %s: %s' % (self.prefix, self.uri)
    def execute(self, graph):
        graph.prefix_to_uri[self.prefix] = self.uri
        
class DefCommand(Command):
    '''Define a function pattern.'''
    def __init__(self, ident, pattern, *triples):
        self.ident = ident
        self.pattern = pattern
        self.triples = triples
    def __str__(self): return '%s %s = %s' % (self.ident, self.pattern, self.triples)
    def execute(self, graph):
        ident = str(self.ident)
        if not ident in graph.defs: graph.defs[ident] = []
        graph.defs[ident] = [(self.pattern, self.triples)] + graph.defs[ident]
        
class CallCommand(Command):
    '''Call a previously defined function.'''
    def __init__(self, ident, pattern):
        self.ident = ident
        self.pattern = pattern
    def __str__(self): return '%s %s' % (self.ident, self.pattern)
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
    '''Import and interpret a Beaver file.'''
    def __init__(self, uri):
        self.uri = uri
    def __str__(self): return '@import %s' % self.uri
    def execute(self, graph):
        try:
            stream = urllib2.urlopen(str(self.uri)[1:-1])
            graph.parse(stream=stream)
        except ValueError:
            with open(str(self.uri)[1:-1], 'r') as stream:
                graph.parse(stream=stream)
        
        
class LoadCommand(Command):
    '''Load an RDF file.'''
    def __init__(self, uri):
        self.uri = uri
    def __str__(self): return '@load %s' % self.uri
    def execute(self, graph):
        import RDF
        
        parser = RDF.Parser('rdfxml')
        try:
            data = urllib2.urlopen(str(self.uri)[1:-1]).read()
        except ValueError:
            with open(str(self.uri)[1:-1], 'r') as handle:
                data = handle.read()
                
        for rdf_statement in parser.parse_string_as_stream(data, str(self.uri)[1:-1]):
            contents = []
            for item in rdf_statement.subject, rdf_statement.predicate, rdf_statement.object:
                if isinstance(item, RDF.Uri): new_item = Uri(str(item))
                elif isinstance(item, RDF.Node): new_item = Uri(str(item))
                contents.append(new_item)
            stmt = Statement(*contents)
            graph.add_stmt(stmt)
            
            
class DelCommand(Command):
    '''Remove triples from the graph.'''
    def __init__(self, triples):
        self.triples = triples
