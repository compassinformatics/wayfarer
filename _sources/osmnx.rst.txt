OSMNx Compatibility
===================

OSMNx brings ability to download OSM data directly into networks, plotting, and isochrone analysis. 

To handle one-way OSMNX adds in all paths twice - once with reverse flag true and once with it set to false. 

An edge is in the following format:

.. sourcecode:: python

    (53128729, 53149520, 0, {'osmid': 6400955, 'name': 'Hill Lane', 'highway': 'residential', 'oneway': False, 'reversed': False, 'length': 118.926})

See loader functions at https://github.com/gboeing/osmnx/blob/c034e2bf670bd8e9e46c5605bc989a7d916d58f3/osmnx/graph.py#L528

.. sourcecode:: python

    [(53017091, 53064327, 0, {'osmid': 6345781, 'name': 'Rose Avenue', 'highway': 'residential', 'oneway': False, 'reversed': False, 'length': 229.891}),
    (53017091, 53075599, 0, {'osmid': 6345781, 'name': 'Rose Avenue', 'highway': 'residential', 'oneway': False, 'reversed': True, 'length': 121.11399999999999,
    'geometry': <LINESTRING (-122.248 37.826, -122.248 37.826, -122.248 37.826, -122.248 37....>}),

Shapely LineStrings support pickling: https://shapely.readthedocs.io/en/stable/geometry.html#pickling
Whereas ``save_graphml`` converts all attributes to strings, including attributes such as ``LEN_`` which wayfarer requires to be numeric.

.. sourcecode:: python

    # ox.save_graphml(G, filepath) # this converts numeric attributes to strings
    # https://github.com/gboeing/osmnx/blob/c123c39e5c69159f87802cd6bf6dd79204019744/osmnx/io.py#L158
    # G = ox.load_graphml(filepath) # this sets the types based on field names

    # geometry is expected as shapely.geometry.linestring.LineString

Nodes are in the format:

.. sourcecode:: python

    (53022625, {'y': 37.8207744, 'x': -122.2323445, 'highway': 'turning_circle', 'street_count': 1})