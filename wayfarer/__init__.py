import sys
from typing import NamedTuple


PY37 = sys.version_info.major == 3 and sys.version_info.minor >= 7

__version__ = "0.9.0"

LENGTH_FIELD = "LEN_"
EDGE_ID_FIELD = "EDGE_ID"
OFFSET_FIELD = "OFFSET"

NODEID_FROM_FIELD = "NODEID_FROM"
NODEID_TO_FIELD = "NODEID_TO"

WITH_DIRECTION_FIELD = "WITH_DIRECTION"

SPLIT_POINT_ID_FIELD = "POINT_ID"
SPLIT_MEASURE_FIELD = "MEASURE"

SPLIT_FLAG = "IS_SPLIT"

# the Edge class

# https://mypy.readthedocs.io/en/stable/kinds_of_types.html#named-tuples


class Edge(NamedTuple):
    """
    A class representing a network edge
    """

    start_node: (int | str)
    end_node: (int | str)
    key: (int | str)
    attributes: dict


def to_edge(edge: tuple) -> Edge:
    """
    Convert a tuple into an Edge namedtuple

    >>> to_edge((0, 1, 1, {"LEN_": 10}))
    Edge(start_node=0, end_node=1, key=1, attributes={'LEN_': 10})

    >>> to_edge((0, 1, 1))
    Edge(start_node=0, end_node=1, key=1, attributes={})
    """
    assert len(edge) >= 3  # edges must have at least a key

    # attributes will be None if tuple is 3 in length
    if len(edge) == 3:
        attributes = {}
    else:
        attributes = edge[3]

    return Edge(
        start_node=edge[0],
        end_node=edge[1],
        key=edge[2],
        attributes=attributes,
    )


def to_edges(edges: tuple) -> list[Edge]:
    """
    Convert a list of tuples to a list of Edges

    >>> tuples = [(0, 1, 1, {"LEN_": 10}), (1, 2, 2, {"LEN_": 20})]
    >>> to_edges(tuples)
    [Edge(start_node=0, end_node=1, key=1, attributes={'LEN_': 10}), \
Edge(start_node=1, end_node=2, key=2, attributes={'LEN_': 20})]
    """
    return [to_edge(edge) for edge in edges]


# if __name__ == "__main__":
#    import doctest

#    doctest.testmod()
#    print("Done!")
