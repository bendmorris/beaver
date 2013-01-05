from types import BeaverException, Variable, Uri, Value, updated_context
from statement import Statement, TripleStatement
from command import Command, PrefixCommand
from parser import parse_string, parse_file, parse_stream
import sys
import urllib2


default = [
           PrefixCommand('rdf', Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#')),
           ]
    

class Graph(object):
    '''A collection of triples.'''
    def __init__(self, verbose=False):
        self.verbose = verbose
    
        self.reinit()
        
        
    def reinit(self):
        self.statements = {}
        self.prefixes = {}
        self.last_subj = None
        self.defs = {}
        
        self.execute(default)


    def add_stmt(self, stmt):
        if self.verbose: print str(stmt)
        
        if stmt.subj == ';': 
            if self.last_subj:
                subj = self.last_subj
            else: raise BeaverException('Unspecified subject: %s' % stmt)
        else: 
            self.last_subj = subj = stmt.subj

        verb = stmt.verb
        obj = stmt.obj
        
        if isinstance(subj, Value): raise BeaverException('Literals are not allowed as RDF subjects.')
        if isinstance(verb, Value): raise BeaverException('Literals are not allowed as RDF predicates.')
        
        for x in (subj, verb, obj):
            if isinstance(x, Variable):
                raise BeaverException('Unresolved variable: %s' % x)
        
        if not subj in self.statements:
            self.statements[subj] = {}
        if not verb in self.statements[subj]: self.statements[subj][verb] = set()
        self.statements[subj][verb].add(stmt.obj)
        
        
    def remove_stmt(self, stmt):
        if self.verbose: print '@del %s' % str(stmt)
        
        if stmt.subj == ';': 
            if self.last_subj:
                subj = self.last_subj
            else: raise BeaverException('Unspecified subject: %s' % stmt)
        else: 
            self.last_subj = subj = stmt.subj
        
        verb = stmt.verb
        obj = stmt.obj
        
        if not subj in self.statements: return
        if not verb in self.statements[subj]: return
        
        try: self.statements[subj][verb].remove(stmt.obj)
        except KeyError: pass
        
        if len(self.statements[subj][verb]) == 0: del self.statements[subj][verb]
        if len(self.statements[subj]) == 0: del self.statements[subj]
        
        
    def execute(self, stmt, context={}):
        if isinstance(stmt, Statement):
            replace = stmt.replace(context, self.defs)
            if replace:
                new_stmt, new_context = replace
                context = updated_context(context, new_context)
                return self.execute(new_stmt, context)
            
            stmt = stmt.as_triple()
            
            self.add_stmt(stmt)
            
            if len(stmt.other_objs) > 0:
                self.execute([Statement(stmt.subj, stmt.verb, o) for o in stmt.other_objs], context)
            
        elif isinstance(stmt, Command):
            replace = stmt.replace(context, self.defs)
            if replace:
                new_stmt, new_context = replace
                context = updated_context(context, new_context)
                return self.execute(new_stmt, context)
        
            stmt.execute(self, context)
            
        elif hasattr(stmt, '__iter__'):
            for substmt in stmt:
                self.execute(substmt, context)
            return
            
        else:
            raise BeaverException('Unrecognized statement: %s' % stmt)
        
        
    def uri(self, uri):
        if hasattr(uri, 'prefix'):
            try:
                base = self.prefixes[uri.prefix]
            except KeyError:
                raise BeaverException('Prefix %s is not defined.' % uri.prefix)
        else: base = ''
        return Uri(base + uri.url)
        
        
    def parse(self, filename=None, text=None, stream=None):
        if filename:
            parsed = parse_file(filename)
        elif text:
            parsed = parse_string(text)
        elif stream:
            parsed = parse_stream(stream)
        else:
            raise BeaverException('Must specify filename, text, or stream to parse.')
        
        stmts = 0
        for stmt, start, end in parsed:
            stmts += 1
            self.execute(stmt)
        
        return stmts
        
        
    def draw(self, filename, use='pydot'):
        if use=='pygraphviz':
            try: import pygraphviz as pgv
            except ImportError: raise BeaverException('pygraphviz is required to draw graphs.')
            
            graph = pgv.AGraph(overlap=False, strict=False)
            
            def format_label(s):
                if isinstance(s, Uri):
                    s = s.apply_prefix(self.prefixes)
                
                s = str(s)
                if s.startswith('<') and s.endswith('>'): s = s[1:-1]
                
                return s

            nodes = set()
            def new_node(s):
                node = format_label(s)
                if not node in nodes:
                    graph.add_node(node)
                    nodes.add(node)
                    
            for s in self.statements:
                new_node(s)
                for v, objs in self.statements[s].items():
                    for o in objs:
                        new_node(o)
                        graph.add_edge(format_label(s), format_label(o), label=format_label(v), dir='forward')
            graph.layout(prog='dot')
            graph.draw(filename)
            
    
        elif use=='pydot':
            try: import pydot
            except ImportError: raise BeaverException('pydot is required to draw graphs.')
            
            graph = pydot.Dot(graph_type='digraph')
            
            def format_node_name(s):
                s = str(s)
                if s.startswith('<') and s.endswith('>'): s = s[1:-1]
                
                bad_chars = "<>'\":"
                for char in bad_chars:
                    s = s.replace(char, '')
                
                return 'x%s' % s
                
            def format_label(s):
                if isinstance(s, Uri):
                    s = s.apply_prefix(self.prefixes)
            
                s = str(s)
                if s.startswith('<') and s.endswith('>'): s = s[1:-1]
                
                if (s.startswith('"') and s.endswith('"')): 
                    s = '"\\"%s\\""' % s[1:-1]
                else:
                    s = '"%s"' % s
                return s
            
            nodes = set()
            def new_node(s):
                node = format_node_name(s)
                label = format_label(s)
                if not node in nodes:
                    graph.add_node(pydot.Node(node, label=label))
                    nodes.add(node)
                    
            for s in self.statements:
                new_node(s)
                for v, objs in self.statements[s].items():
                    for o in objs:
                        new_node(o)
                        graph.add_edge(pydot.Edge(format_node_name(s), format_node_name(o), label=format_label(v)))
                        
            img_format = filename.split('.')[-1]
            graph.write(filename, format=img_format)
            
            
    def write(self, filename=None):
        if filename is None:
            handle = sys.stdout
        else:
            try:
                handle = urllib2.urlopen(filename, 'w')
            except ValueError:
                handle = open(filename, 'w')
                
        if self.prefixes:
            handle.write('\n'.join(['@prefix %s: %s' % (key, value) for key, value in self.prefixes.items()]))
            handle.write('\n\n')
        
        newline = False
        for subj in self.statements:
            if newline: handle.write('\n')
            else: newline = True

            semicolon = False
            for verb in self.statements[subj]:
                if semicolon: s = ' ;\n    '
                else: s = subj.apply_prefix(self.prefixes); semicolon = True
                
                v = verb.apply_prefix(self.prefixes)
                if v == 'rdf:type': v = 'a'
                
                objs = self.statements[subj][verb]
                o = ', '.join([str(obj.apply_prefix(self.prefixes)) for obj in objs])
                handle.write('%s %s %s' % (s, v, o))
            handle.write(' .\n')
