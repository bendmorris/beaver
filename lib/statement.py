from types import BeaverException, Variable, Pattern, EmptyPattern, updated_context
from copy import deepcopy as copy


class Statement(object):
    '''A generic statement containing any number of variable parts.'''
    def __init__(self, subject, verb_objects):
        self.subject = subject
        self.verb_objects = verb_objects
    def __str__(self): 
        return '%s %s .' % (str(self.subject),
                             ' ; '.join(['%s %s' % (str(verb), 
                                                     ', '.join([str(o) for o in objects]))
                                          for verb, objects in self.verb_objects])
                             )
    def __repr__(self): return str(self)
    def __eq__(self, x): return str(self) == str(x)
    
    """def replace(self, *varsets):
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
                                if isinstance(definition, tuple): definition = list(definition)
                                
                                if isinstance(definition, Statement): definition = definition.parts
                                elif isinstance(definition, list): definition = [p for stmt in definition for p in stmt.parts]
                                else: definition = [definition]
                                
                                self.parts = self.parts[:n] + definition + self.parts[n+1:]
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

        
        return None"""
        
                            
def match(given, definition):
    '''Returns true if a given argument matches the definition.'''
    if isinstance(definition, Variable): return True
    return definition == given
