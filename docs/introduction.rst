wayfarer
========

Features:

+ Uses reverse_lookup for faster access of edge by key
+ Supports line directions
+ Supports all networkx algorithms


-------------------------------------------------------------------------------------------------------- benchmark: 2 tests --------------------------------------------------------------------------------------------------------
Name (time in ns)                                   Min                    Max                  Mean                StdDev                Median                 IQR            Outliers  OPS (Kops/s)            Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_lookup_speed_with_reverse_lookup          300.0000 (1.0)      53,900.0000 (1.0)        447.2362 (1.0)        455.2966 (1.0)        400.0000 (1.0)      100.0000 (1.0)      824;3686    2,235.9549 (1.0)      192308           1
test_lookup_speed_without_reverse_lookup     2,100.0000 (7.00)     60,300.0000 (1.12)     2,343.6191 (5.24)     1,012.9738 (2.22)     2,300.0000 (5.75)     100.0000 (1.0)      470;1928      426.6905 (0.19)      46083           1
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Additional "keys" dict associated with the graph

{
 12345: (0, 100),
 12346: (100, 0)
}

Places in code to check for this and keep it updated:

        if "keys" in net.graph.keys():

Use Cases
---------



Edge Class
----------

    >>> to_edge((0, 1, 1, {"LEN_": 10}))
    Edge(start_node=0, end_node=1, key=1, attributes={'LEN_': 10})


Requires Python 3.10
Use of annotations:

| was added in python 3.10, so not available in python 3.8.
