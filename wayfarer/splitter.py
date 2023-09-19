"""
This module handles splitting existing edges, and creating new nodes
to join the split edges
"""
import logging
import uuid
from collections import defaultdict, OrderedDict
from wayfarer import functions, linearref
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
    GEOMETRY_FIELD,
    Edge,
)

log = logging.getLogger("wayfarer")

SPLIT_KEY_SEPARATOR = "::"


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

    # if geometry is being stored in the edge then create a new line
    # based on the offset
    if GEOMETRY_FIELD in atts:
        edge_id = atts[EDGE_ID_FIELD]
        ls = atts[GEOMETRY_FIELD]
        log.debug(f"Creating split geometry from {from_m} to {to_m} on {edge_id}")
        cut_line = linearref.create_line(ls, from_m, to_m)
        atts[GEOMETRY_FIELD] = cut_line

    return atts


def create_split_key(key: (str | int), m: (float | int), precision=3) -> str:
    """
    Function to ensure a standard format for split keys
    using the key of an edge and a measure
    E.g. "123829::154.2"
    The ``SPLIT_KEY_SEPARATOR`` can be used to find split keys
    in the network

    >>> create_split_key(123829, 154.22384972623, precision=3)
    '123829::154.224'
    >>> create_split_key(123829, 154.2)
    '123829::154.2'
    >>> create_split_key(123829, 154, precision=3)
    '123829::154'
    >>> SPLIT_KEY_SEPARATOR in "123829::154.2"
    True
    """

    # display with 3 decimal places, but remove any trailing zeros
    # and decimal place if a round number
    measure = f"{m:.{precision}f}".rstrip("0").rstrip(".")
    return f"{key}{SPLIT_KEY_SEPARATOR}{measure}"


def check_split_edges(split_edges: list[Edge]):
    # all edges should have the split flag
    is_split = [e.attributes[SPLIT_FLAG] for e in split_edges]
    assert set(is_split) == {True}

    # all edges should have the same original EdgeId
    edge_ids = [e.attributes[EDGE_ID_FIELD] for e in split_edges]
    assert len(set(edge_ids)) == 1

    return True


def get_split_nodes(split_edges: list[Edge]) -> list[int | str]:
    """
    Get the unique list of split nodes associated
    with the collection of edges

    Args:
        split_edges: a list of split edges that make up a single full edge

    Returns:
        A unique list of split nodes
    """
    nodes = []
    split_nodes = []

    for split_edge in split_edges:
        nodes += [split_edge.start_node, split_edge.end_node]

    for n in set(nodes):
        if SPLIT_KEY_SEPARATOR in str(n):
            split_nodes.append(n)

    return split_nodes


def get_measures_from_split_edges(split_edges: list[Edge]):
    """
    From a collection of split edges, get all the measures
    that the original edge was split
    Split nodes are in the form '2::60' (using the ``SPLIT_KEY_SEPARATOR``)

    Args:
        split_edges: a list of split edges that make up a single full edge

    Returns:
        The measures used to split the original edge
    """

    check_split_edges(split_edges)
    measures = []
    split_nodes = get_split_nodes(split_edges)

    for n in split_nodes:
        m_val = float(str(n).split(SPLIT_KEY_SEPARATOR)[1])
        measures.append(m_val)

    return measures


def unsplit_network_edges(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), split_edges: list[Edge]
) -> Edge:
    """
    Take a list of split network edges and join them back together
    to form the original edge. Split keys and nodes are removed from the network.
    This function can be used to then resplit the edge in different locations
    or add additional splits

    Args:
        net (object): a networkx network
        split_edges: a list of split edges that make up a single full edge

    Returns:
        The unsplit edge

    """

    check_split_edges(split_edges)

    # get all lengths
    original_length = sum([e.attributes[LENGTH_FIELD] for e in split_edges])

    # get first edge
    first_edge = min(split_edges, key=lambda e: e.attributes[OFFSET_FIELD])
    start_node = first_edge.attributes[NODEID_FROM_FIELD]
    edge_id = first_edge.attributes[EDGE_ID_FIELD]

    # get last edge
    last_edge = max(split_edges, key=lambda e: e.attributes[OFFSET_FIELD])
    end_node = last_edge.attributes[NODEID_TO_FIELD]

    # remove the split edges from the network

    for split_edge in split_edges:
        functions.remove_edge_by_key(net, split_edge.key)

    split_nodes = get_split_nodes(split_edges)

    # clean-up the split nodes - removing a node however removes
    # any connecting edges which will lead to errors, so check they are orphaned
    for n in split_nodes:
        if net.degree(n) == 0:
            net.remove_node(n)

    # copy across any attributes from the original edge
    atts = first_edge.attributes.copy()

    atts.update(
        {
            EDGE_ID_FIELD: edge_id,
            LENGTH_FIELD: original_length,
            NODEID_FROM_FIELD: start_node,
            NODEID_TO_FIELD: end_node,
        }
    )

    atts.pop(SPLIT_FLAG)
    atts.pop(OFFSET_FIELD)

    # the add_edge function takes care of adding the edge_id back to the keys
    new_edge = functions.add_edge(net, start_node, end_node, edge_id, atts)

    return new_edge


def split_network_edge(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    key: (str | int),
    measures: list[int | float],
) -> list[Edge]:
    """
    Split a network edge based on a list of measures.
    We can also split a split edge but this relies on knowing the key of the
    split edge and measures would need to reflect the length of the new edge
    rather than the original edge.

    Args:
        net (object): a networkx network
        key: the key of the edge to be split
        measures: a list of measures where the line should be split

    Returns:
        A list of the new edges created by splitting
    """

    new_edges = []

    original_edge = functions.get_edge_by_key(net, key, with_data=True)

    original_length = original_edge.attributes[LENGTH_FIELD]

    validated_measures = []

    for m in measures:
        if m >= original_length:
            log.debug(
                f"Split measure {m} is greater or equal to the length {original_length} of edge {key}"
            )
        elif m <= 0:
            log.debug("Split measure is 0 or less - no need to split!")
        else:
            validated_measures.append(m)

    if len(validated_measures) == 0:
        log.debug("No measures along line - returning original edges")
        return [original_edge]

    log.debug(f"Splitting {original_edge.key} with {len(measures)} points")

    functions.remove_edge_by_key(net, original_edge.key)
    prev_node = original_edge.start_node
    from_m = 0  # type: (int | float)

    for to_m in sorted(set(validated_measures)):
        split_key = create_split_key(key, to_m)
        atts = get_split_attributes(
            original_edge.attributes, from_m, to_m, prev_node, split_key
        )
        new_edge = functions.add_edge(net, prev_node, split_key, split_key, atts)
        new_edges.append(new_edge)
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
    new_edge = functions.add_edge(
        net, prev_node, original_edge.end_node, split_key, atts
    )
    new_edges.append(new_edge)

    return new_edges


def get_measure_for_point(line, pt):
    snapped_input_point, dist = linearref.get_nearest_vertex(pt, line)
    log.debug(f"Input point {dist:.5f} from line")
    measure = linearref.get_measure_on_line(line, snapped_input_point)
    return measure


def get_split_node_for_measure(network_edge, length, measure):
    if abs(length - measure) < 0.001:
        # don't split at the end of the line
        node_id = network_edge.end_node
    elif abs(measure - 0) < 0.001:
        # don't split at the start of the line
        node_id = network_edge.start_node
    else:
        # a new split node is created
        node_id = create_split_key(network_edge.key, measure)

    return node_id
