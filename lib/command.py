from types import BeaverException, Variable, Uri, Pattern, EmptyPattern, updated_context
from statement import Statement
import urllib2
from copy import deepcopy as copy


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
        if graph.verbose: print str(self)
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
        if graph.verbose: print str(self)
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
        if graph.verbose: print str(self)
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
        if graph.verbose: print str(self)
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
    def __str__(self): return '@del %s' % self.triples
    def __repr__(self): return str(self)
    def execute(self, graph, context={}, triples=None):
        if triples is None: triples = self.triples
        if not hasattr(triples, '__iter__'): triples = [triples]
        
        for stmt in triples:
            replace = stmt.replace(context, graph.defs)
            if replace: pass
            
            stmt = stmt.as_triple()
            
            graph.remove_stmt(stmt)
            
            if len(stmt.other_objs) > 0:
                self.execute(graph, context, [Statement(stmt.subj, stmt.verb, o) for o in stmt.other_objs])
        
        
class DrawCommand(Command):
    '''Remove triples from the graph.'''
    def __init__(self, uri):
        self.uri = uri
    def __str__(self): return '@draw %s' % self.uri
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        if graph.verbose: print str(self)
        graph.draw(filename=str(self.uri)[1:-1])
        
        
class OutCommand(Command):
    '''Write triples to output file.'''
    def __init__(self, uri=None):
        self.uri = uri
    def __str__(self): return '@out%s' % ('' if self.uri is None else ' %s' % self.uri)
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        if graph.verbose: print str(self)
        graph.write(filename=None if self.uri is None else str(self.uri)[1:-1])
        
        
class ReinitCommand(Command):
    '''Remove triples from the graph.'''
    def __str__(self): return '@reinit'
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        if graph.verbose: print str(self)
        graph.reinit()
        
        
class ForCommand(Command):
    def __init__(self, ident, sequence, *expression):
        self.ident = ident
        self.sequence = sequence
        self.expression = expression
    def __str__(self): return '@for %s in (%s ) %s' % (self.ident, self.sequence, ''.join([str(x) for x in self.expression]))
    def __repr__(self): return str(self)
    def execute(self, graph, context={}):
        if graph.verbose: print str(self)
        for var in self.sequence.vars:
            expr = [copy(x) for x in self.expression]
            iter_context = {self.ident: [(EmptyPattern, var)]}
            new_context = updated_context(context, iter_context)
            graph.execute(expr, new_context)
