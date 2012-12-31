from types import BeaverException, Variable, Pattern, EmptyPattern, updated_context
from copy import deepcopy as copy


class Statement(object):
    '''A generic statement containing any number of variable parts.'''
    def __init__(self, *parts):
        self.parts = parts
    def __str__(self): 
        return (' '.join([str(part) for part in self.parts[:3]]) + 
                ''.join([', %s' % part for part in self.parts[3:]]))
    def __repr__(self): return str(self)
    def __eq__(self, x): return str(self) == str(x)
    
    def as_triple(self): return TripleStatement(*self.parts)
    
    def replace(self, *varsets):
        '''Checks each part of the statement against defined variables. If any
        matches are found, the statement is updated. If the statement is a function
        call, a new set of statements is returned; otherwise, None is returned.'''
        matched = False
        
        # check for single variables in statement
        for n, part in enumerate(self.parts):
            if isinstance(part, Variable):
                for varset in varsets:
                    if matched: break
                    if part in varset:
                        defs = varset[part]
                        for (pattern, definition) in defs:
                            if matched: break
                            if part == definition: continue
                            
                            if len(pattern.vars) == 0:
                                definition = copy(definition)
                                
                                # a match was found; replace the variable with its definition
                                if isinstance(definition, Statement): definition = definition.parts
                                elif isinstance(definition, list): definition = [p for stmt in definition for p in stmt.parts]
                                else: definition = [definition]
                                
                                self.parts = self.parts[:n] + tuple(definition) + self.parts[n+1:]
                                matched = True
                
        # repeat until no changes were made
        if matched: return self.replace(*varsets)
        
        # check if statement is a function call
        if isinstance(self.parts[0], Variable):
            var = self.parts[0]
            args = self.parts[1:]
            for varset in varsets:
                if var in varset:
                    defs = varset[var]
                    for (pattern, definition) in defs:
                        need_to_match = pattern.vars
                        if len(need_to_match) == len(args):
                            if all(match(arg, m) for arg, m in zip(args, need_to_match)):
                                # a match was found; return a function call with a new context
                                context = {}
                                
                                for arg, m in zip(args, need_to_match):
                                    if isinstance(m, Variable):
                                        context[m] = [(EmptyPattern, arg)]
                                        
                                return (copy(definition), updated_context(varsets[0], context))

        
        return None
        
                            
def match(given, definition):
    '''Returns true if a given argument matches the definition.'''
    if isinstance(definition, Variable): return True
    return definition == given


class TripleStatement(Statement):
    '''Statements can be evaluated to become triple statements.'''
    def __init__(self, *parts):
        if len(parts) < 3: raise BeaverException('A triple statement needs a subject, predicate, and object. %s' % str(Statement(*parts)))
        triple = parts[:3]
        #for t in triple:
        #    if isinstance(t, Variable): raise BeaverException('Undefined variable: %s' % t)
        self.subj, self.verb, self.obj = triple
        self.other_objs = parts[3:]
    def __str__(self): return '%s %s %s' % (self.subj, self.verb, ', '.join([str(self.obj)] + [str(o) for o in self.other_objs])) 
    def __repr__(self): return str(self)
    def as_triple(self): return self
