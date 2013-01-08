from types import BeaverException, Variable, Collection, EmptyCollection, updated_context
from copy import deepcopy as copy


class Statement(object):
    '''A generic statement containing any number of variable parts.'''
    def __init__(self, subject, verb_objects):
        self.subject = subject
        self.verb_objects = [(v, list(o)) for v, o in verb_objects]
    def __str__(self): 
        return '%s %s .' % (str(self.subject),
                             ' ; '.join(['%s %s' % (str(verb), 
                                                     ', '.join([str(o) for o in objects]))
                                          for verb, objects in self.verb_objects])
                             )
    def __repr__(self): return str(self)
    def __eq__(self, x): return str(self) == str(x)
    
    def replace(self, *varsets):
        '''Checks each part of the statement against defined variables. If any
        matches are found, the statement is updated. If the statement is a function
        call, a new set of statements is returned; otherwise, None is returned.'''
        matched = False
        
        # check for single variables in statement
        subj = self.subject
        if isinstance(subj, Variable):
            result, new_match = def_match(subj, varsets)
            if result:
                self.subject = new_match
                return self.replace(*varsets)        
        
        for n, (verb, objects) in enumerate(self.verb_objects):
            if isinstance(verb, Variable):
                result, new_match = def_match(verb, varsets)
                if result:
                    v, o = self.verb_objects[n]
                    self.verb_objects[n] = (new_match, o)
                    return self.replace(*varsets)
        
            for m, obj in enumerate(objects):
                if isinstance(obj, Variable):
                    result, new_match = def_match(obj, varsets)
                    if result:
                        objects[m] = new_match
                        return self.replace(*varsets)
        
        return None
        
                            
def match(given, definition):
    '''Returns true if a given argument matches the definition.'''
    if isinstance(definition, Variable): return True
    return definition == given
    
def def_match(part, varsets):
    matched = False
    
    for varset in varsets:
        if matched: break
        if part in varset:
            defs = varset[part]
            for (pattern, definition) in defs:
                if matched: break
                if part == definition: continue
                
                if pattern is None:
                    definition = copy(definition)
                    
                    # a match was found; replace the variable with its definition
                    if isinstance(definition, tuple): definition = list(definition)
                    
                    return (True, definition)
    return (False, None)
