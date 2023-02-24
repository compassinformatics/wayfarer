import logging
import networkx
import wayfarer
from math import hypot
from wayfarer import (
    EDGE_ID_FIELD,
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
)
from wayfarer import functions
import pickle
from typing import Iterable


log = logging.getLogger("wayfarer")


class UniqueDict(dict):
    """
    A subclass of dict to ensure all keys are unique
    """

    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)
        else:
            raise KeyError("The key {} already exists. Keys must be unique".format(key))


def distance(
    p1: tuple[(int | float), (int | float)], p2: tuple[(int | float), (int | float)]
) -> float:
    """
    Return the Euclidean distance between two points
    Ignore any Z values associated with the points

    >>> distance((0, 0), (10, 10))
    14.142135623730951
    """

    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return hypot(x2 - x1, y2 - y1)


def save_network_to_file(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), filename: str
):
    """
    Save a network to a Python pickle file
    Note these cannot be shared between different versions of Python
    """

    with open(filename, "wb") as f:
        pickle.dump(net, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_network_from_file(
    filename: str,
) -> (networkx.MultiGraph | networkx.MultiDiGraph):
    """
    Return a network previously saved to a pickle file
    """
    with open(filename, "rb") as f:
        return pickle.load(f)


def add_edge(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), properties: dict
) -> (str | int):
    """
    Add a new edge to a network based on a dict containing
    the required wayfarer fields
    """

    key = properties[EDGE_ID_FIELD]
    start_node = properties[NODEID_FROM_FIELD]
    end_node = properties[NODEID_TO_FIELD]

    # key is used to identify different edges between nodes
    net.add_edge(start_node, end_node, key=key, **properties)

    # update the reverse lookup dictionary attached to the graph
    # this is used for fast edge_id lookups
    # the key is the dict key and the values are the nodes

    if "keys" in net.graph.keys():
        net.graph["keys"][key] = (start_node, end_node)

    return key


def create_graph(
    use_reverse_lookup: bool,
    graph_type: (networkx.MultiGraph | networkx.MultiDiGraph) = networkx.MultiGraph,
) -> (networkx.MultiGraph | networkx.MultiDiGraph):
    """
    Create a new networkx graph, with an optional dictionary to store unique keys
    for fast edge lookups
    """
    if graph_type not in (networkx.MultiDiGraph, networkx.MultiGraph):
        raise ValueError(
            "The graph type {} unsupported. Only MultiGraph and MultiDiGraph are supported".format(
                graph_type.__name__
            )
        )

    graph_name = "Wayfarer Generated {} (version {})".format(
        graph_type.__name__, wayfarer.__version__
    )

    if use_reverse_lookup:
        reverse_lookup = UniqueDict()
        net = graph_type(name=graph_name, keys=reverse_lookup)
    else:
        net = graph_type(name=graph_name)
    return net


def load_network_from_records(
    recs: Iterable,
    key_field: str = EDGE_ID_FIELD,
    length_field: str = LENGTH_FIELD,
    from_field: str = NODEID_FROM_FIELD,
    to_field: str = NODEID_TO_FIELD,
    use_reverse_lookup: bool = True,
    graph_type: (networkx.MultiGraph | networkx.MultiDiGraph) = networkx.MultiGraph,
) -> (networkx.MultiGraph | networkx.MultiDiGraph):
    """
    Create a new networkX graph based on a list of dictionary objects
    containing the required wayfarer properties
    """

    # simple dict type record

    net = create_graph(use_reverse_lookup, graph_type)

    for r in recs:

        try:
            key = r[key_field]
            start_node = r[from_field]
            end_node = r[to_field]
            len_ = r[length_field]
        except KeyError:
            log.error("Available properties: {}".format(",".join(r.keys())))
            raise

        network_attributes = {
            EDGE_ID_FIELD: key,
            LENGTH_FIELD: len_,
            NODEID_FROM_FIELD: start_node,
            NODEID_TO_FIELD: end_node,
        }

        field_names = [key_field, length_field, from_field, to_field]
        all(map(r.pop, field_names))  # remove all keys already added
        network_attributes.update(r)  # add in any remaining keys

        add_edge(net, network_attributes)

    return net


def load_network(
    recs: Iterable,
    key_field: str = EDGE_ID_FIELD,
    length_field: str = LENGTH_FIELD,
    use_reverse_lookup: bool = True,
    graph_type: (networkx.MultiGraph | networkx.MultiDiGraph) = networkx.MultiGraph,
    skip_errors: bool = False,
    strip_properties: bool = False,
) -> (networkx.MultiGraph | networkx.MultiDiGraph):
    """
    Create a new networkX graph using a list of recs of type __geo_interface__
    This allows networks to be created using libraries such as Fiona

    strip_properties can be used to reduce the size of the network file by only
    retaining the properties required to run routing
    """

    net = create_graph(use_reverse_lookup, graph_type)
    error_count = 0

    for r in recs:

        # __geo__interface
        geom = r["geometry"]
        coords = geom["coordinates"]

        if geom["type"] != "LineString":
            if skip_errors is True:
                error_count += 1
                continue
            else:
                raise ValueError(
                    "The geometry type {} is not supported - only LineString can be used".format(
                        geom["type"]
                    )
                )

        properties = r["properties"]

        if length_field in properties:
            length = properties[length_field]
        else:
            length = sum([distance(*combo) for combo in functions.pairwise(coords)])

        try:
            key = int(properties[key_field])
        except KeyError:
            log.error("Available properties: {}".format(",".join(properties.keys())))
            raise

        start_node = coords[0]
        end_node = coords[-1]

        network_attributes = {
            EDGE_ID_FIELD: key,
            LENGTH_FIELD: length,
            NODEID_FROM_FIELD: start_node,
            NODEID_TO_FIELD: end_node,
        }

        # only use fields required for routing
        if strip_properties is True:
            properties = network_attributes
        else:
            properties.update(network_attributes)

        add_edge(net, properties)

    if error_count > 0:
        log.warning("{} MultiLineString features were ignored".format(error_count))

    return net


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    print("Done!")
