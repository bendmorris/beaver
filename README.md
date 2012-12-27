Beaver is a semantic programming language. It accepts and manipulates data in the form of RDF graphs.

Currently, Beaver is an interpreted superset of the Turtle RDF specification. (RDF/XML support is planned.)
Therefore, any valid Turtle file is also valid Beaver code.

Other commands include:

    # open another Beaver file and parse the results into the current graph
    @import <uri>
    
    # define and call functions
    ?create_edge ?child ?parent ?edge = {
        ?child <part_of_edge> ?edge .
        ?parent <part_of_edge> ?edge .
        ?edge <has_parent> ?parent ;
              <has_child> ?child .
    }
    
    ?create_edge <node1> <node2> <edge1> .


Using the interpreter, you can save an image of the resulting graph:

    beaver -d test.png -e "<ben> a <human> ; <likes> <carol> ; <likes> <football> . <carol> a <human> ; <likes> <ben> ; <likes> <anime> . <ruben> a <human> ; a <baby> ."

![beaver graph](http://i.imgur.com/A067V.jpg)
