from types import BeaverException, Variable, Uri, Pattern, EmptyPattern, updated_context
from statement import Statement
import urllib2
import copy


class Command(object):
    def execute(self, graph, context={}):
        raise BeaverException('This command (%s) has not yet been implemented.' % self.__doc__)
    def __str__(self): return '%s(**%s)' % (str(self.__class__.__name__).split('.')[-1], self.__dict__)
    def __repr__(self): return str(self)
    def replace(self, *varsets): pass
        
        
class PrefixCommand(Command):
    '''Define a URI prefix.'''
    def __init__(self, prefix, uri):
        self.prefix = prefix
        self.uri = uri
    def __str__(self): return '@prefix %s: %s' % (self.prefix, self.uri)
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        graph.prefixes[self.prefix] = self.uri
        
        
class DefCommand(Command):
    '''Define a function pattern.'''
    def __init__(self, ident, pattern, *triples):
        self.ident = ident
        self.pattern = pattern
        self.triples = triples
    def __str__(self):
        if hasattr(self.triples, '__iter__'): triples = '{ %s }' % ' '.join([str(s) for s in self.triples])
        else: triples = str(self.triples)
        return '%s%s = %s' % (self.ident, self.pattern, triples)
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        ident = self.ident
        if not ident in graph.defs: graph.defs[ident] = []
        graph.defs[ident] = [(self.pattern, self.triples)] + graph.defs[ident]
        
        
class ImportCommand(Command):
    '''Import and interpret a Beaver file.'''
    def __init__(self, uri):
        self.uri = uri
    def __str__(self): return '@import %s' % self.uri
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
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
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
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
            graph.add_stmt(stmt.as_triple())
            
            
class DelCommand(Command):
    '''Remove triples from the graph.'''
    def __init__(self, triples):
        self.triples = triples
    def __str__(self): return '@del %s' % triples
    def __repr__(self): return str(self)
        
        
class DrawCommand(Command):
    '''Remove triples from the graph.'''
    def __init__(self, uri):
        self.uri = uri
    def __str__(self): return '@draw %s' % self.uri
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        graph.draw(filename=str(self.uri)[1:-1])
        
        
class ReinitCommand(Command):
    '''Remove triples from the graph.'''
    def __str__(self): return '@reinit'
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        graph.reinit()
        
        
class ForCommand(Command):
    def __init__(self, ident, sequence, *expression):
        self.ident = ident
        self.sequence = sequence
        self.expression = expression
    def __str__(self): return '@for %s in (%s) %s' % (self.ident, self.sequence, ''.join([str(x) for x in self.expression]))
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        for var in self.sequence.vars:
            expr = [copy.copy(x) for x in self.expression]
            iter_context = {self.ident: [(EmptyPattern, var)]}
            new_context = updated_context(context, iter_context)
            graph.execute(expr, new_context)
