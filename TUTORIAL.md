Data and code in Beaver are statements that map onto RDF graphs, and the 
syntax is a superset of the Turtle RDF serialization format.

Beaver files contain series of semantic statements. These statements contain a
subject, a predicate (describing a relationship), and an object. Each statement
describes how its subject is related to its object; in other words, it 
describes a property of the subject. For example, the statement:

    <whiskers> <color> <black> .

...says that the subject, `<whiskers>`, has a `<color>`, which is `<black>`.
This is represented graphically by an arrow, "color", pointing from "whiskers"
to "black":

![beaver graph](http://i.imgur.com/fVNXI.jpg)    

If a statement contains more than three parts, the additional parts represent 
additional objects: subject, predicate, object1, object2...

Each part of a statement can be either a literal (e.g. `"abc"` or `1.0` or `3`) 
or a  URI (represented in angled brackets: `<http://www.example.org/cat>`.) 
Statements can optionally be followed by a period to avoid ambiguity.

To avoid having to spell out long URIs repeatedly, prefixes can be defined:
    
    @prefix example: <http://www.example.org/>
    example:cat <is> <cool> .

`example:cat` now refers to the longer URI `<http://www.example.org/cat>`.

The word `a` refers to the predicate `rdf:type` and represents the type of an 
object:

    <whiskers> a example:cat .

`<whiskers>` is now an object of type `<http://www.example.org/cat>`.

Consecutive statements referring to the same subject can use a semicolon;
statements with the same subject and verb, but different objects, can use 
commas. For example:

    <whiskers> a example:cat ;
              <age> 4 ;
              <sex> "female" ;
              <nickname> "Fluffy", "Kitty" .

All of these statements relate to the subject, `<whiskers>`. Whiskers is a cat,
is 4 years old, is female, and has two nicknames, "Fluffy" and "Kitty".

Blocks of statements are delineated by curly brackets:

    {
        <a> <b> <c> .
        <d> <e> <f> .
        <g> <h> <i> .
    }

Variables can be defined using question marks:

    ?a = <whiskers> .
    ?a a example:cat .

The first statement here defines the variable `?a` as referring to 
`<whiskers>`. In the second statement, the `?a` will be replaced by 
`<whiskers>`.

Functions can be declared in the same way. Beaver is a lazy functional language
with pattern matching.

    ?cat ?name = {
        ?name a example:cat .
        <ben> <has_cat> ?name .
    }

    ?cat <whiskers> .
    ?cat <socks> .

Here, the `?cat` function is defined and then called with `?name = <whiskers>` 
and `?name = <socks>`.

Pattern matching means you can declare multiple versions of a function with the
same name but different sets of input. The inputs don't have to be variables.
For example:

    ?is_it_a_one ?b = { ?b <is_a_one> "no" }
    ?is_it_a_one 1 = { 1 <is_a_one> "yes" }

The second definition will only match `?is_it_a_one 1`, while the first 
definition will match `?is_it_a_one` followed by any single input. More recent 
function definitions take precedence. When `?is_it_a_one` is called, it will 
check each definition (in reverse order) until it finds a match.

For loops can be used to iterate over a sequence:

    @for ?name in ('whiskers' 'socks' 'oreo') ?cat ?name .