Data and code in Beaver are statements that map onto RDF graphs, and the 
syntax is a superset of the Turtle RDF serialization format.

Beaver files contain series of semantic statements. These statements contain a
subject, a predicate (describing a relationship), and an object. If a statement
contains more than three parts, the additional parts represent additional 
objects: subject, predict, object1, object2...

Each part of a statement can be either a literal (e.g. "abc" or 1.0 or 3) or a 
URI (represented in angled brackets: <http://www.example.org/cat>. Statements 
can optionally be followed by a period to avoid ambiguity.

To avoid having to spell out long URIs repeatedly, prefixes can be defined:
    
    @prefix example: <http://www.example.org/>
    example:cat <is> <cool> .

"example:cat" now refers to the longer URI <http://www.example.org/cat>.

The word "a" refers to the predicate rdf:type and represents the type of an 
object:

    <whiskers> a example:cat .

Whiskers is now an object of type <http://www.example.org/cat>.

Consecutive statements referring to the same subject can use a semicolon, e.g.:

    <whiskers> a example:cat ;
              <age> 4 ;
              <sex> "female" .

All of these statements relate to the subject, <whiskers>. Whiskers is a cat,
is 4 years old, and is female.

Blocks of statements are delineated by curly brackets:

    {
        <a> <b> <c> .
        <d> <e> <f> .
        <g> <h> <i> .
    }

Variables can be defined using question marks:

    ?a = <whiskers> .
    ?a a example:cat .

The first statement here defines the variable "?a" as referring to <whiskers>.
In the second statement, the ?a will be replaced by <whiskers>.

Functions can be declared in the same way. Beaver is a lazy functional language
with pattern matching.

    ?cat ?name = {
        ?name a example:cat .
        <ben> <has_cat> ?name .
    }

    ?cat <whiskers> .
    ?cat <socks> .

Here, the ?cat function is defined and then called with ?name = <whiskers> and
?name = <socks>.

For loops can be used to iterate over a sequence.

    @for ?name in ('whiskers' 'socks' 'oreo') ?cat ?name .