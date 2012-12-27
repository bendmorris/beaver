Beaver is a semantic programming language. It accepts and manipulates data in the form of RDF graphs.

To install, navigate to the source directory and run "python setup.py install".

Currently, Beaver is an interpreted superset of the Turtle RDF serialization format. Therefore, any valid 
Turtle file is also valid Beaver code. RDF/XML can also be loaded using the @load command (requires librdf,
the Redland RDF library's Python bindings: http://librdf.org/docs/python.html).


Examples of Beaver commands:

    # open another Beaver or Turtle file (local or online) and parse the results into the current graph
    @import <data_file.ttl>

    # load RDF/XML file
    @load <http://www.nexml.org/nexml/examples/trees.rdf>

    # reinitialize everything
    @reinit
    
    # define and call functions
    ?create_edge ?child ?parent ?edge = {
        ?child <part_of_edge> ?edge .
        ?parent <part_of_edge> ?edge .
        ?edge <has_parent> ?parent ;
              <has_child> ?child .
    }
    
    ?create_edge <node1> <node2> <edge1> .
    ?create_edge <node2> <node3> <edge2> .

    # save the current graph as an image file
    @draw <test.png>
    @draw <test2.jpg>

    # remove triples from the graph
    @del <node1> <part_of_edge> <edge1> .


Using the interpreter, you can save images of the resulting graphs (requires pydot or pygraphviz.) For example:

    beaver -d test.png -e "<ben> a <human> ; <likes> <carol>, <football> . <carol> a <human> ; <likes> <ben>, <anime> . <ruben> a <human>, <baby> ."

![beaver graph](http://i.imgur.com/A067V.jpg)

Beaver is written in Python and can also be used as a Python library, e.g.:

    from beaver import Graph
    
    graph = Graph()
    graph.parse(text='<beaver> <is> <great> .')
    
    graph.draw('output.png')