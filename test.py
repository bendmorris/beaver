import lib.parser as p
from lib.graph import Graph

graph = Graph()
graph.parse('test.bvr')

#print graph.__dict__
graph.draw('test.png')
