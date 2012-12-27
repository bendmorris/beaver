Beaver is a semantic programming language. It accepts and manipulates data in the form of RDF graphs.

To install, navigate to the source directory and run "python setup.py install".

Currently, Beaver is an interpreted superset of the Turtle RDF specification. (RDF/XML support is planned.)
Therefore, any valid Turtle file is also valid Beaver code.

Other commands include:

    # open another Beaver file (local or online) and parse the results into the current graph
    @import <uri>
    
    # define and call functions
    ?create_edge ?child ?parent ?edge = {
        ?child <part_of_edge> ?edge .
        ?parent <part_of_edge> ?edge .
        ?edge <has_parent> ?parent ;
              <has_child> ?child .
    }
    
    ?create_edge <node1> <node2> <edge1> .
    ?create_edge <node2> <node3> <edge2> .


Using the interpreter, you can save an image of the resulting graph. For example:

    beaver -d test.png -e "<ben> a <human> ; <likes> <carol>, <football> . <carol> a <human> ; <likes> <ben>, <anime> . <ruben> a <human>, <baby> ."

![beaver graph](http://i.imgur.com/A067V.jpg)
