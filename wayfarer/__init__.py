import sys
from collections import namedtuple


PY37 = sys.version_info.major == 3 and sys.version_info.minor >= 7

__version__ = "0.8.5"

LENGTH_FIELD = "LEN_"
EDGE_ID_FIELD = "EDGE_ID"
OFFSET_FIELD = "OFFSET"

NODEID_FROM_FIELD = "NODEID_FROM"
NODEID_TO_FIELD = "NODEID_TO"

WITH_DIRECTION_FIELD = "WITH_DIRECTION"

SPLIT_POINT_ID_FIELD = "POINT_ID"
SPLIT_MEASURE_FIELD = "MEASURE"

# the Edge class

fields = ("start_node", "end_node", "key", "attributes")
defaults = (None,) * len(fields)
if PY37:
    Edge = namedtuple("Edge", fields, defaults=(None,) * len(fields))
else:
    Edge = namedtuple("Edge", fields)
    Edge.__new__.__defaults__ = (None,) * len(Edge._fields)


def to_edges(edges):
    return [
        Edge(
            start_node=edge[0],
            end_node=edge[1],
            key=edge[2][EDGE_ID_FIELD],
            attributes=edge[2],
        )
        for edge in edges
    ]
