from types import Statement, BeaverException, Variable
from command import Command
from parser import parse_string, parse_file, parse_stream


class Graph(object):
    '''A collection of triples.'''
    def __init__(self, verbose=False):
        self.verbose = verbose
    
        self.statements = {}
        self.prefix_to_uri = {}
        self.last_subj = None
        
        self.parse(filename='default.bvr')
        
        self.defs = {}

    def add_stmt(self, stmt):
        if stmt.subj == ';': 
            subj = self.last_subj
        else: 
            self.last_subj = subj = stmt.subj
        
        subj = str(subj)
        verb = str(stmt.verb)
        obj = stmt.obj
        
        if not subj in self.statements:
            self.statements[subj] = {}
        if not verb in self.statements[subj]: self.statements[subj][verb] = []
        self.statements[subj][verb] += stmt.obj
        
        if self.verbose: print '%s .' % stmt
        
    def execute(self, stmt, context={}):
        if isinstance(stmt, Statement):
            for part in ['subj', 'verb', 'obj']:
                if isinstance(getattr(stmt, part), Variable):
                    id = str(getattr(stmt, part))
                    if id in context: setattr(stmt, part, context[id])
                    elif id in self.defs: setattr(stmt, part, defs[id])
                    else: raise BeaverException('Undefined variable: %s' % id)
            self.add_stmt(stmt)
        elif isinstance(stmt, Command):
            if self.verbose: print str(stmt)
            stmt.execute(self)
        elif hasattr(stmt, '__iter__'):
            for substmt in stmt:
                self.execute(substmt, context)
        else:
            raise BeaverException('Unrecognized statement: %s' % stmt)
        
    def uri(self, uri):
        if hasattr(uri, 'prefix'):
            try:
                base = self.prefix_to_uri[uri.prefix]
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
        
        for stmt, start, end in parsed:
            self.execute(stmt)
        
    def draw(self, filename, use='pydot'):
        if use=='pygraphviz':
            try: import pygraphviz as pgv
            except ImportError: raise BeaverException('pygraphviz is required to draw graphs.')
            
            graph = pgv.AGraph(overlap=False, strict=False)
            
            def format_label(s):
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
