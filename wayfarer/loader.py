import logging
import wayfarer
from math import hypot
from wayfarer import (
    EDGE_ID_FIELD,
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    GEOMETRY_FIELD,
)
from wayfarer import functions
import pickle
from typing import Iterable
from networkx import MultiGraph, MultiDiGraph


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
    Return the Euclidean distance between two points.
    Any z-values associated with the points are ignored.

    Args:
        p1: The first point
        p2: The second point
    Returns:
        The distance between the two points

    >>> distance((0, 0), (10, 10))
    14.142135623730951
    """

    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return hypot(x2 - x1, y2 - y1)


def save_network_to_file(net: (MultiGraph | MultiDiGraph), filename: str) -> None:
    """
    Save a network to a Python pickle file
    Note these cannot be shared between different versions of Python

    Args:
        net: The network
        filename: The filename to save the network as a pickle file

    """

    with open(filename, "wb") as f:
        pickle.dump(net, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_network_from_file(
    filename: str,
) -> (MultiGraph | MultiDiGraph):
    """
    Return a network previously saved to a pickle file

    Args:
        filename: The filename to the pickle file containing the network
    Returns:
        The network

    """
    with open(filename, "rb") as f:
        return pickle.load(f)


def add_edge(net: (MultiGraph | MultiDiGraph), properties: dict) -> (str | int):
    """
    Add a new edge to a network based on a dict containing
    the required wayfarer fields

    Args:
        net: A network
        properties: A dictionary containing values for the edge
    Returns:
        The key of the edge

    >>> net = MultiGraph()
    >>> add_edge(net, {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 1})
    1
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
    use_reverse_lookup: bool = True,
    graph_type: (MultiGraph | MultiDiGraph) = MultiGraph,
) -> (MultiGraph | MultiDiGraph):
    """
    Create a new networkx graph, with an optional dictionary to store unique keys
    for fast edge lookups

    >>> net = create_graph()

    Args:
        use_reverse_lookup: Create a dictionary for fast key lookup
        graph_type: The type of network
    Returns:
        The new network
    """
    if graph_type not in (MultiDiGraph, MultiGraph):
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
    use_reverse_lookup: bool = True,
    graph_type: (MultiGraph | MultiDiGraph) = MultiGraph,
    key_field: str = EDGE_ID_FIELD,
    length_field: str = LENGTH_FIELD,
    from_field: str = NODEID_FROM_FIELD,
    to_field: str = NODEID_TO_FIELD,
) -> (MultiGraph | MultiDiGraph):
    """
    Create a new networkX graph based on a list of dictionary objects
    containing the required wayfarer properties

    >>> recs = [{"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 2, "LEN_": 5, "PROP1": "A"}]
    >>> net = load_network_from_records(recs)
    >>> str(net)  # doctest: +ELLIPSIS
    "MultiGraph named 'Wayfarer Generated MultiGraph (version ...)' with 2 nodes and 1 edges"

    Args:
        recs: An iterable of dictionary objects The filename to the pickle file containing the network
        use_reverse_lookup: Create a dictionary as part of the graph that stores unique edge keys for
                            fast lookups
        graph_type: The type of network to create
    Returns:
        A new network

    """

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


def load_network_from_geometries(
    recs: Iterable,
    use_reverse_lookup: bool = True,
    graph_type: (MultiGraph | MultiDiGraph) = MultiGraph,
    skip_errors: bool = False,
    strip_properties: bool = False,
    keep_geometry: bool = False,
    key_field: str = EDGE_ID_FIELD,
    length_field: str = LENGTH_FIELD,
    rounding: int = 5,
) -> (MultiGraph | MultiDiGraph):
    """
    Create a new networkX graph using a list of recs of type ``__geo_interface__``
    This allows networks to be created using libraries such as Fiona.
    Any ``MultiLineString`` geometries in the network will be ignored, geometries should
    be converted to ``LineString`` prior to creating the network.

    >>> rec = {"geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]}, "properties": {"EDGE_ID": 1}}
    >>> net = load_network_from_geometries([rec])
    >>> str(net)  # doctest: +ELLIPSIS
    "MultiGraph named 'Wayfarer Generated MultiGraph (version ...)' with 2 nodes and 1 edges"

    Args:
        recs: An iterable of dictionary objects The filename to the pickle file containing the network
        use_reverse_lookup: Create a dictionary as part of the graph that stores unique edge keys for
                            fast lookups
        graph_type: The type of network to create
        skip_errors: Ignore any geometries that are not of type ``LineString``
        strip_properties: Reduce the size of the network file by only retaining the
                          properties required to run routing. Any other properties in the records
                          will be ignored
        key_field: A key field containing a unique Id for each feature must be provided
        length_field: The field in the geometry properties that contains a length. If not provided
                      then the length will be calculated from the geometry. It is assumed the geometry
                      is projected, as a simple planar distance will be calculated.
        rounding: If no node fields are used then nodes will be created based on the start and end points of
                  the input geometries. As node values must match exactly for edges to be connected rounding
                  to a fixed number of decimal places avoids unconnected edges to to tiny differences in floats
                  e.g. (-9.564484483347517, 52.421103202488965) and (-9.552925853749544, 52.41969110706263)
    Returns:
        A new network
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

        if key_field == "id" and "id" in r:
            key = int(r["id"])
        else:
            try:
                key = int(properties[key_field])
            except KeyError:
                log.error(
                    "Available properties: {}".format(",".join(properties.keys()))
                )
                raise

        # if we simply take the coordinates then often these differ due to rounding issues as they
        # are floats e.g. (-9.564484483347517, 52.421103202488965) and (-9.552925853749544, 52.41969110706263)
        # instead convert the coordinates to unique strings, apply rounding, and strip any z-values

        start_node = "{}|{}".format(
            round(coords[0][0], rounding), round(coords[0][1], rounding)
        )
        end_node = "{}|{}".format(
            round(coords[-1][0], rounding), round(coords[-1][1], rounding)
        )

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

        if keep_geometry:
            properties[GEOMETRY_FIELD] = geom

        add_edge(net, properties)

    if error_count > 0:
        log.warning("{} MultiLineString features were ignored".format(error_count))

    return net
