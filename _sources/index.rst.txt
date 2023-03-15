Wayfarer
========

Overview
--------


A Python library for creating and analysing geospatial networks using `NetworkX <https://networkx.org/>`_.


Uses shortest routes to provide a user interface quickly mark up linear features. 


For an overview presentation see https://compassinformatics.github.io/wayfarer-presentation/


Focus on creating user interfaces for selecting linear features such as roads and rivers in a network.

+ Works with any data source (database, flat files, dictionaries)
+ Compatibility with osmnx
+ Access to all of the NetworkX `Algorithms <https://networkx.org/documentation/latest/reference/algorithms/index.html>`_

Allow an easy user interface for marking up features on linear referenced features.

Linear referencing is a powerful technique used in Geographic Information Systems (GIS) to locate geographic features and events along a 
linear feature such as a road, river or pipeline.

+ Easy analysis and reporting of data along linear features
+ Efficient data storage - no need to duplicate linear features

More familiar with Python than Postgres and SQL


pgRouting:

requires users to have a good understanding of SQL, PostGIS, and network analysis concepts. This can make it difficult for beginners to get started.
PgRouting is designed to work with PostgreSQL and PostGIS, so users may need to convert their data to these formats before they can use the tool. This can be time-consuming and may require additional software or expertise.

GraphHopper
OSRM

Network Analyst is an extension for ArcGIS 

networkx

https://pypi.org/project/pyroutelib3/ - OSM data

PyRoutelib: PyRoutelib is a Python library for network routing that is built on top of NetworkX. It includes a range of routing algorithms, including Dijkstra's algorithm and A* search, as well as tools for working with routing profiles and generating directions. PyRoutelib is designed to be easy to use and can be integrated into other Python projects.
osmnx: OSMnx is a Python library for working with OpenStreetMap data and generating street networks. It includes tools for routing and network analysis, including shortest-path algorithms and tools for calculating network measures such as centrality and betweenness. OSMnx can be used to generate routing networks for a range of use cases, including transportation planning and urban design.
pandana: Pandana is a Python library for working with large-scale spatial networks, including road networks and public transit networks. It includes tools for network analysis and routing, as well as tools for generating spatial aggregates and conducting spatial queries. Pandana is designed to be fast and memory-efficient, making it well-suited for large-scale routing applications

https://pypi.org/project/pandana/

Dynamic splitting - accessibility scenarios. Changes to isochrones. 

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   self
   examples.rst
   solver.rst
   api/functions.rst
   api/loader.rst
   api/linearref.rst
   api/routing.rst

..
    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
