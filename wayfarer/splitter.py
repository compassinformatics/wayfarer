"""
This module handles splitting existing edges, and creating new nodes
to join the split edges
"""
import logging
import uuid
from collections import defaultdict, OrderedDict
from wayfarer import functions
import networkx
from wayfarer import (
    LENGTH_FIELD,
    OFFSET_FIELD,
    EDGE_ID_FIELD,
    SPLIT_FLAG,
    SPLIT_POINT_ID_FIELD,
    SPLIT_MEASURE_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    Edge,
)

log = logging.getLogger("wayfarer")


def create_node_id(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), point_id: (str | int)
):

    # if point_id in net.nodes():
    #    raise ValueError("The point ID {} already exists as a Node Id in the network".format(point_id))
    return point_id


def create_unique_join_node() -> str:
    """
    Create a unique GUID for the join node
    """

    return str(uuid.uuid4())


def group_measures_by_edge(input):

    res = OrderedDict()

    for edge_id, measure in input:
        if edge_id in res:
            res[edge_id].append(measure)
        else:
            res[edge_id] = [measure]
    return res


def split_with_points(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    recs: list[dict],
    edge_id_field: str = EDGE_ID_FIELD,
    point_id_field: str = SPLIT_POINT_ID_FIELD,
    measure_field: str = SPLIT_MEASURE_FIELD,
):
    """
    Join a list of point records to a network, creating a new "join"
    edge

    recs is a list of dict objects that should have at a minimum the following
    fields [{"EDGE_ID": 1, "POINT_ID": 1, "MEASURE": 10.0}]
    Any additional fields will be added as properties to the new line
    """

    # first we'll group all points for each edge

    edge_splits = defaultdict(list)

    for r in recs:

        edge_id, point_id, measure = (
            r[edge_id_field],
            r[point_id_field],
            r[measure_field],
        )
        split_node = create_split_key(edge_id, measure)
        unique_edge_key = create_unique_join_node()
        from_node = create_node_id(net, point_id)

        # set the nodes as attributes so we can calculate the direction if required
        r[NODEID_FROM_FIELD] = from_node
        r[NODEID_TO_FIELD] = split_node

        # here we create a new edge joining the point to attach to the network
        # to a new node on the split line represented by the line id and measure along
        edge = Edge(
            start_node=from_node, end_node=split_node, key=unique_edge_key, attributes=r
        )

        functions.add_edge(net, **edge._asdict())  # unpack namedtuple to **kwargs
        edge_splits[edge_id].append(measure)

    for edge_id, measures in edge_splits.items():
        split_network_edge(net, edge_id, measures)


def get_split_attributes(
    original_attributes: dict,
    from_m: (float | int),
    to_m: (float | int),
    start_node: (str | int | None) = None,
    end_node: (str | int | None) = None,
) -> dict:
    """
    For a part of an edge that has been split
    update its attributes so the length is correct
    and any start and end nodes stored in the attributes table
    are correct

    >>> atts = {"OFFSET": 10, "LEN_": 100}
    >>> get_split_attributes(atts, 50, 70)
    {'OFFSET': 60, 'LEN_': 20, 'IS_SPLIT': True}
    """
    atts = original_attributes.copy()
    atts[LENGTH_FIELD] = to_m - from_m

    if OFFSET_FIELD in original_attributes:
        offset = original_attributes[
            OFFSET_FIELD
        ]  # when using a cumulative measure along a feature
    else:
        offset = 0

    atts[OFFSET_FIELD] = from_m + offset

    # update the nodes if provided and the fields are part of the list of attributes
    if start_node and end_node:
        if all(p in atts for p in [NODEID_FROM_FIELD, NODEID_TO_FIELD]):
            atts[NODEID_FROM_FIELD] = start_node
            atts[NODEID_TO_FIELD] = end_node

    # now add a flag to indicate this edge has been split
    atts[SPLIT_FLAG] = True
    return atts


def create_split_key(key: (str | int), m: (float | int)) -> str:
    """
    Function to ensure a standard format for split keys
    using the key of an edge and a measure
    E.g. (154.2, 123829)
    """
    return f"{key}:{m:g}"


def split_network_edge(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    key: (str | int),
    measures: list[int | float],
) -> (networkx.MultiGraph | networkx.MultiDiGraph):
    """
    Specify the key to be certain the correct edge is removed
    Measures is a flat list
    We can split a split edge but this relies on knowing the keys
    Measures would be wrong as m values against original segment
    """
    log.debug("Splitting line with %i points", len(measures))

    original_edge = functions.get_edge_by_key(net, key, with_data=True)
    net.remove_edge(original_edge.start_node, original_edge.end_node, original_edge.key)

    if "keys" in net.graph.keys():
        del net.graph["keys"][key]

    original_length = original_edge.attributes[LENGTH_FIELD]

    # measures = sorted(measures)

    for m in measures:
        if m >= original_length:
            raise ValueError(
                "Split measure {} is greater or equal to the edge length {}".format(
                    m, original_length
                )
            )
        if m == 0:
            raise ValueError("Split measure is 0 - no need to split!")

    prev_node = original_edge.start_node
    from_m = 0  # type: (int | float)

    for to_m in sorted(set(measures)):
        split_key = create_split_key(key, to_m)
        atts = get_split_attributes(
            original_edge.attributes, from_m, to_m, prev_node, split_key
        )
        functions.add_edge(net, prev_node, split_key, split_key, atts)
        from_m, prev_node = to_m, split_key

    # add final part
    atts = get_split_attributes(
        original_edge.attributes,
        from_m,
        original_length,
        prev_node,
        original_edge.end_node,
    )
    split_key = create_split_key(key, original_length)
    functions.add_edge(net, prev_node, original_edge.end_node, split_key, atts)

    return net
