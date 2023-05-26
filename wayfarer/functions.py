"""
This module contains functions related to networks and routing
"""
import itertools
import copy
import logging
from collections import OrderedDict
import networkx
from wayfarer import loops
from typing import Iterable


from wayfarer import (
    EDGE_ID_FIELD,
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    WITH_DIRECTION_FIELD,
    OFFSET_FIELD,
    Edge,
)


log = logging.getLogger("wayfarer")


def pairwise(iterable) -> Iterable[tuple]:
    """
    Loops through the iterable, returning adjacent pairs
    each time. Useful for returning point coordinates.

    >>> list(pairwise((0, 10, 20, 30)))
    [(0, 10), (10, 20), (20, 30)]
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def get_unique_ordered_list(items: Iterable) -> list:
    """
    An order-preserving function to get a unique list of edges or nodes

    >>> get_unique_ordered_list([1, 1, 2, 3, 4, 5, 6, 5])
    [1, 2, 3, 4, 5, 6]

    Args:
        items: Any iterable
    Returns:
        A list of unique values
    """
    return list(dict.fromkeys(items))


def edges_to_graph(edges: (list[Edge] | list[tuple])) -> networkx.MultiGraph:
    """
    Utility function to create a new MultiGraph based on a list of edges

    Args:
        edges: A list of Edge named tuples, or simply tuples
    Returns:
        A new network

    >>> edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {})]
    >>> net = edges_to_graph(edges)
    >>> print(net)
    MultiGraph with 3 nodes and 2 edges
    """
    net = networkx.MultiGraph()

    for edge in edges:
        if len(edge) > 2:
            net.add_edge(edge[0], edge[1], key=edge[2], attributes=edge[3])
        else:
            # when no key is provided networkx uses a 0 value for the key
            net.add_edge(edge[0], edge[1])

    return net


def add_edge(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    start_node: (int | str),
    end_node: (int | str),
    key: (int | str),
    attributes: dict,
) -> Edge:
    """
    Add an edge to a network. When adding an edge to a network, nodes are automatically
    added

    Args:
        net: A network
        start_node: The start node of the edge
        end_node: The end node of the edge
        key: The unique key of the edge
        attributes: Any attributes associated with the edge

    >>> net = networkx.MultiGraph()
    >>> add_edge(net, 1, 2, "A", {"LEN_": 10})
    Edge(start_node=1, end_node=2, key='A', attributes={'LEN_': 10})
    >>> print(net)
    MultiGraph with 2 nodes and 1 edges
    """
    new_edge = Edge(start_node, end_node, key, attributes)
    net.add_edge(
        new_edge.start_node, new_edge.end_node, new_edge.key, **new_edge.attributes
    )

    if "keys" in net.graph.keys():
        # we are using a reverse lookup dict so update this also
        net.graph["keys"][key] = (start_node, end_node)

    return new_edge


def remove_edge_by_key(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), key: (int | str)
):
    edge = get_edge_by_key(net, key, with_data=False)
    net.remove_edge(edge.start_node, edge.end_node, key=edge.key)

    # remove from the keys dictionary if it exists
    if "keys" in net.graph.keys():
        del net.graph["keys"][key]


def get_edge_by_key(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    key: (int | str),
    with_data: bool = True,
) -> Edge:
    """
    Go through all edge property dicts until the relevant key is found
    Using an iterator faster than list comprehension
    See https://stackoverflow.com/a/36413569/179520 answer from networkx dev

    https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.edges.html

    400ns with reverse lookup
    1.16 seconds with generators

    >>> edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {"LEN_": 10})]
    >>> net = edges_to_graph(edges)
    >>> get_edge_by_key(net, "B", with_data=True)
    Edge(start_node=1, end_node=2, key='B', attributes={'attributes': {'LEN_': 10}})
    """

    if "keys" in net.graph:
        # this uses the reverse lookup approach of storing a dict containing the keys
        # as part of the graph
        nodes = net.graph["keys"].get(key, None)
    else:
        # otherwise we loop through all edges until the key is found
        gen = ((u, v) for u, v, k in net.edges(keys=True) if k == key)
        nodes = next(gen, None)  # min 1.17s

    if nodes is None:
        raise KeyError(f"The edge with key {key} was not found in the network")

    u, v = nodes

    try:
        if with_data:
            atts = net[u][v][key]
            edge = Edge(u, v, key, atts)
        else:
            edge = Edge(u, v, key, {})
    except KeyError:
        log.warning(
            f"The edge with start_node: {u} end_node: {v} key: {key} could not be found in the network"
        )
        raise

    return edge


def get_edges_by_attribute(net, attribute_field: str, value) -> Iterable[Edge]:
    """
    Go through all edge property dicts until the relevant attribute is found.
    Edges can have different attribute dicts, so add a check that the key exists
    If the attribute_field does not exist for a particular edge then it is ignored.
    Returns an iterator
    """

    return (
        Edge(u, v, k, d)
        for u, v, k, d in net.edges(keys=True, data=True)
        if attribute_field in d and d[attribute_field] == value
    )


# def get_edge_by_keys(net, keys, key_field=EDGE_ID_FIELD):
#    #  set(a).intersection(b)
#    return (
#        (u, v) for u, v, key_value in net.edges(data=key_field) if key_value in keys
#    )


def get_all_complex_paths(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), node_list
):
    """
    For a node path, find any self-looping edges on a node
    and add these combinations to the possible path list
    """

    # first find any nodes with a self-loop
    loop_nodes = []

    for n in node_list:
        if get_edges_from_node_pair(net, n, n):
            loop_nodes.append(n)

    # see https://stackoverflow.com/a/62665978/179520

    if not loop_nodes:
        paths = [node_list]
    else:
        paths = []

        for ln in range(len(loop_nodes) + 1):
            for loop_subset in itertools.combinations(loop_nodes, ln):
                paths.append(
                    sorted(
                        node_list + list(loop_subset), key=lambda i: node_list.index(i)
                    )
                )

    return paths


def get_all_paths_from_nodes(net, node_list, with_direction_flag=False):
    """
    Get all combinations of edges along a set of nodes, rather
    than just the shortest edges
    l = [("a","b"), ("c"), ("d","e")]
    [('a', 'c', 'd'), ('a', 'c', 'e'), ('b', 'c', 'd'), ('b', 'c', 'e')]

    list(itertools.combinations([[1],[1,2]], r=2))
    [([1], [1, 2])]

    Check for self loops on every node
    """

    all_paths = []

    node_paths = get_all_complex_paths(net, node_list)

    # TODO cleanup messy loop check
    for np in list(node_paths):
        if len(set(np)) > 2:
            sn, en = np[0], np[-1]
            if sn != en:
                edges = get_edges_from_node_pair(net, sn, en, hide_log_output=True)
                if edges:
                    # there is an edge between the start and end of the path
                    # possible loop
                    extra_path = list(np)
                    extra_path.append(sn)
                    node_paths.append(extra_path)

    for node_path in node_paths:
        node_pairs = list(pairwise(node_path))

        path_list = []
        for u, v in node_pairs:  # loop through all pairs and get all edges between them
            node_edges = []
            edges = get_edges_from_node_pair(net, u, v)

            if edges:
                for key, attributes in edges.items():
                    # make a copy so client programs can modify without
                    # affecting the original edge dict
                    atts_copy = copy.deepcopy(attributes)
                    edge = Edge(start_node=u, end_node=v, key=key, attributes=atts_copy)
                    if with_direction_flag:
                        add_direction_flag(
                            **edge._asdict()
                        )  # unpack namedtuple to **kwargs

                    node_edges.append(edge)

            path_list.append(node_edges)

        # use product to get every combination of edges between the nodes
        combinatations = itertools.product(*path_list)
        all_paths.append(combinatations)

    # return a flat list of paths
    return itertools.chain(*all_paths)


def get_path_length(path_edges):
    return sum([edge.attributes[LENGTH_FIELD] for edge in path_edges])


def get_edges_from_node_pair(
    net, start_node: (int | str), end_node: (int | str), hide_log_output: bool = False
) -> networkx.classes.coreviews.AtlasView | None:
    """
    Get all edges between two nodes

    This function can return multiple edges when there is more than
    one edge between two nodes

    >>> net = networkx.MultiGraph()
    >>> net.add_edges_from([(0, 1, "A", {'val': 'foo'}), (0, 1, "B", {'val': 'bar'})])
    ['A', 'B']
    >>> get_edges_from_node_pair(net, start_node=0, end_node=1)
    AtlasView({'A': {'val': 'foo'}, 'B': {'val': 'bar'}})
    """

    if start_node == end_node:  # do not warn when checking for loops
        hide_log_output = True

    try:
        edges = net[start_node][end_node]
    except KeyError:
        if hide_log_output is False:
            log.debug("Could not find edge (%s, %s)", start_node, end_node)
        edges = None

    return edges


def get_edges_from_nodes(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    node_list: list[int | str],
    with_direction_flag: bool = False,
    length_field: str = LENGTH_FIELD,
    return_unique: bool = True,
) -> list[Edge]:
    """
    From a list of nodes, create pairs and then get the shortest edge between the two nodes
    Set with_direction_flag to add a new attribute to the edge to show if it is matching the
    direction of the path
    """
    edge_list = []

    node_pairs = pairwise(node_list)

    for u, v in node_pairs:
        edges = get_edges_from_node_pair(net, u, v)
        if edges:
            key, attributes = get_shortest_edge(edges, length_field)
            atts_copy = copy.deepcopy(attributes)
            edge = Edge(start_node=u, end_node=v, key=key, attributes=atts_copy)

            if with_direction_flag:
                add_direction_flag(**edge._asdict())  # unpack namedtuple to **kwargs

            edge_list.append(edge)

    if return_unique:
        return list({v.key: v for v in edge_list}.values())
    else:
        return edge_list


def get_shortest_edge(edges: dict, length_field=LENGTH_FIELD):
    """
    From a dictionary of edges, get the shortest edge
    by its length
    If two edges have identical lengths then the edge with the higher Id
    will be returned
    """

    if not edges:
        raise ValueError("The edge list is empty")

    min_key = min(
        edges, key=lambda k: edges[k][length_field]
    )  # py3 can add default=None
    return min_key, edges[min_key]


def add_direction_flag(start_node, end_node, attributes, **kwargs):
    """
    kwargs so an edge with any properties can be easily passed to the function
    """

    if not attributes:
        log.warning(
            "Cannot set the direction flag without an attributes dictionary for the edge"
        )
        return

    if NODEID_FROM_FIELD not in attributes:
        log.warning(
            "{} missing in the edge attributes. Cannot set direction.".format(
                NODEID_FROM_FIELD
            )
        )
        return

    if NODEID_TO_FIELD not in attributes:
        log.warning(
            "{} missing in the edge attributes. Cannot set direction.".format(
                NODEID_TO_FIELD
            )
        )
        return

    nodeid_from = attributes[NODEID_FROM_FIELD]
    nodeid_to = attributes[NODEID_TO_FIELD]

    if (nodeid_from, nodeid_to) == (start_node, end_node):
        # with direction
        attributes[WITH_DIRECTION_FIELD] = True
    else:
        assert (nodeid_to, nodeid_from) == (start_node, end_node)
        # against direction
        attributes[WITH_DIRECTION_FIELD] = False


def get_nodes_from_edges(edges):
    """
    From a list of edges return a unique, ordered list
    of nodes along the path
    """
    all_nodes = []
    for edge in edges:
        edge_atts = edge.attributes
        nodes = [edge_atts[NODEID_FROM_FIELD], edge_atts[NODEID_TO_FIELD]]
        if edge_atts[WITH_DIRECTION_FIELD] is False:
            nodes = reversed(nodes)

        all_nodes += nodes

    # return a unique ordered list
    return list(OrderedDict.fromkeys(all_nodes))


def get_unattached_node(net, edge):
    """
    Given an edge find which end is unattached on the
    network
    If the edge is part of a loop then return the start node
    If the edge is attached at both ends then None is returned
    """

    start_node, end_node = edge[0], edge[1]

    start_degrees = net.degree(start_node)
    end_degrees = net.degree(end_node)

    if start_degrees == 1:
        unattached_node = start_node
    elif end_degrees == 1:
        unattached_node = end_node
    else:
        if loops.has_loop(net):
            log.debug("The network is a loop")
            # return arbitrary node in this case
            unattached_node = start_node
        else:
            log.debug("Both ends of the edge are attached")
            unattached_node = None

    return unattached_node


def get_sink_nodes(net):
    """
    Get all the sinks in the network.

    out_degree_iter is the number of edges pointing out of the node
    http://networkx.lanl.gov/reference/generated/networkx.DiGraph.out_degree_iter.html

    Args:
        net (object): a networkx network

    Returns:
        sinks (list): a list of sink nodes [(0,1), (1,0)]
    """
    sinks = [node for node, degree in net.out_degree() if degree == 0]
    return sinks


def get_sink_edges(net):
    """
    Get all the sinks edges in the network. These are edges which have no edges attached
    at their downstream end

    Args:
        net (object): a networkx network

    Returns:
        end_edges (dict): a dict containing sink segment codes and their associated network edge
    """
    sinks = get_sink_nodes(net)

    return get_edges(net, sinks)


def get_source_nodes(net):
    """
    Get all the source in the network.

    in_degree_iter is the number of edges pointing into of the node
    http://networkx.lanl.gov/reference/generated/networkx.DiGraph.in_degree_iter.html

    Args:
        net (object): a networkx network

    Returns:
        sinks (list): a list of sink nodes [(0,1), (1,0)]
    """
    sources = [node for node, degree in net.in_degree() if degree == 0]
    return sources


def get_source_edges(net):
    """
    Get all the source edges in the network. These are edges which have no edges attached
    at their upstream end

    Args:
        net (object): a networkx network

    Returns:
        end_edges (dict): a dict containing source segment codes and their associated network edge
    """
    sources = get_source_nodes(net)

    return get_edges(net, sources)


def get_edges(net, nodes):
    """
    Get all the edges in the network that touch the nodes in the
    nodes list. Note only works with DiGraph or MultiDiGraph.

    Args:
        net (object): a networkx network
        nodes: (list):  a list of network nodes e.g. ``[(224966, 437657), (225195, 437940)]``

    Returns:
        end_edges (dict): a dict containing segment codes and their associated network edge
    """

    end_edges = {}

    for node in nodes:
        in_edges = net.in_edges(node)

        for edge in in_edges:
            edges = get_edges_from_node_pair(net, edge[0], edge[1])
            assert len(edges) == 1
            end_edges.update(edges)

    return end_edges


def get_ordered_end_nodes(edges: list[Edge], end_nodes: list) -> list[int]:
    """
    Ensures the end nodes are returned in the same order as the input edges

    >>> edges = [Edge(1 , 2, "A", {}), Edge(1, 0, "B", {})]
    >>> nodes = [0, 1]
    >>> get_ordered_end_nodes(edges, nodes)
    [1, 0]
    """

    # create a list of nodes from edges
    edge_nodes = [(e[0], e[1]) for e in edges]
    edge_nodes_list = list(sum(edge_nodes, ()))

    # sort the end nodes by their index in this list
    end_nodes.sort(key=lambda n: edge_nodes_list.index(n))
    return end_nodes


def get_end_nodes(edges, ordered: bool = True) -> list:
    """
    Find the end nodes of a graph

    >>> edges = [Edge(0 , 1, "A", {}), Edge(1, 2, "B", {})]
    >>> get_end_nodes(edges)
    [0, 2]
    """

    net = edges_to_graph(edges)
    out_degree = dict(net.degree())

    for n in net.nodes():
        log.debug(("Node connections for {}: {}".format(n, out_degree[n])))

    end_nodes = [n for n in out_degree if out_degree[n] == 1]

    if ordered:
        end_nodes = get_ordered_end_nodes(edges, end_nodes)

    return end_nodes


def get_multiconnected_nodes(edges, connections=2):
    """
    Get all nodes which have at least n connections

    >>> edges = [Edge(0 , 1, "A", {}), Edge(1, 2, "B", {})]
    >>> get_multiconnected_nodes(edges, connections=2)
    [1]
    """

    net = edges_to_graph(edges)
    out_degree = dict(net.degree())
    multiconnected_nodes = [n for n in out_degree if out_degree[n] >= connections]
    return multiconnected_nodes


def has_overlaps(edges: list[Edge]) -> bool:
    """
    Checks if the provided list of edges has overlaps
    If an edge is split but the measures don't overlap then this will return False
    The same edge id can be found at the start and end of the sequence if there is
    no overlap of measures

    >>> edges = [Edge(0, 1, "A", {"EDGE_ID": 1, "OFFSET": 0, "LEN_": 10}), \
Edge(1, 2, "B", {"EDGE_ID": 2, "OFFSET": 0, "LEN_": 10})]
    >>> has_overlaps(edges)
    False
    """
    # get the edge id from the attributes rather than the edge key in case
    # there are split edges which will have modified keys

    sorted_edges = sorted(edges, key=lambda e: e.attributes[EDGE_ID_FIELD])
    grouped_edges = itertools.groupby(
        sorted_edges, key=lambda e: e.attributes[EDGE_ID_FIELD]
    )

    for _, edge_group in grouped_edges:
        for edge1, edge2 in itertools.combinations(edge_group, 2):

            from_m1 = edge1.attributes.get(OFFSET_FIELD, 0)
            to_m1 = from_m1 + edge1.attributes.get(LENGTH_FIELD, 0)

            from_m2 = edge2.attributes.get(OFFSET_FIELD, 0)
            to_m2 = from_m2 + edge2.attributes.get(LENGTH_FIELD, 0)

            if max(from_m1, from_m2) < min(to_m1, to_m2):
                return True

    return False
