Creating Networks
=================

Each source and fields are different so load these outside project. 

Field names mapping as dict if not using standard?

https://stackoverflow.com/questions/12496089/how-can-i-override-a-constant-in-an-imported-python-module

Put in __init__.py


Load with NODEID_FROM and TO when checking to see if with or against direction in a networkx.MultiGraph()

If the line dataset does not contain attribute fields containing a nodeid from and a nodeid to, then the geometry
can be used instead, by using objects that use the ``__geo_interface__``, see `here <https://gist.github.com/sgillies/2217756>`_
for more details.

If the ``fiona`` library is used then all records returned implement this interface.


``key_field`` must be an integer field, with no null values.

MultiLineStrings
----------------

Note that only LineStrings are supported by the wayfarer library - any MultiLineStrings must be split into simple LineStrings
before attempting to create a network. This is because each edge in the network can only have a single start and end node.


Multipart to singleparts
This algorithm takes a vector layer with multipart geometries and generates a new one in which all geometries 
contain a single part. Features with multipart geometries are divided in as many different features as parts the geometry
contain, and the same attributes are used for each of them.



File Geodatabase Example
------------------------

