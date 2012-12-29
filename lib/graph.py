from types import BeaverException, Variable, Uri, updated_context
from statement import Statement, TripleStatement
from command import Command
from parser import parse_string, parse_file, parse_stream



default = '''
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix bvr: <http://www.beaver-lang.org/1/0/0/syntax#> .
'''
    

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
        
        self.parse(text=default)


    def add_stmt(self, stmt):
        if stmt.subj == ';': 
            if self.last_subj:
                subj = self.last_subj
            else: raise BeaverException('Unspecified subject: %s' % stmt)
        else: 
            self.last_subj = subj = stmt.subj
        
        verb = stmt.verb
        obj = stmt.obj
        
        if not subj in self.statements:
            self.statements[subj] = {}
        if not verb in self.statements[subj]: self.statements[subj][verb] = set()
        self.statements[subj][verb].add(stmt.obj)
        
        if self.verbose: print str(stmt)
        
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
        
            if self.verbose: print str(stmt)
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
