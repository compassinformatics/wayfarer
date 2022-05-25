import itertools
import copy
import logging
from collections import OrderedDict
import networkx


from wayfarer import (
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    WITH_DIRECTION_FIELD,
    Edge,
)

try:
    from itertools import izip as zip
except ImportError:  # will be 3.x series
    pass


log = logging.getLogger("wayfarer")


def pairwise(iterable):
    """
    Loops through the iterable, returning adjacent pairs
    each time. Useful for returning point coordinates.
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def add_edge(net, start_node, end_node, key, attributes):
    """
    When adding an edge to a network, nodes are automatically
    added
    """
    net.add_edge(start_node, end_node, key=key, **attributes)

    if "keys" in net.graph.keys():
        # we are using a reverse lookup dict so update this also
        net.graph["keys"][key] = (start_node, end_node)


def get_edge_by_key(net, key, with_data=True, with_direction=False):
    """
    Go through all edge property dicts until the relevant key is found
    Iterator faster than list comprehension
    See https://stackoverflow.com/a/36413569/179520 answer from networkx dev

    https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.edges.html

    400ns with reverse lookup
    1.16 seconds with generators

    The WITH_DIRECTION flag will always be true here - it simply creates the key in the attributes
    """

    if "keys" in net.graph:
        nodes = net.graph["keys"].get(key, None)
    else:
        gen = ((u, v) for u, v, k in net.edges(keys=True) if k == key)
        nodes = next(gen, None)  # min 1.17s

    if nodes is None:
        raise KeyError("The edge with key {} was not found in the network".format(key))

    u, v = nodes

    if with_data:
        atts = net[u][v][key]
        edge = Edge(u, v, key, atts)
    else:
        edge = Edge(u, v, key, None)

    if with_direction:
        add_direction_flag(**edge._asdict())
    return edge


def get_edge_by_attribute(net, value, attribute_field):
    """
    Go through all edge property dicts until the relevant attribute is found
    Return an iterator
    For getting data see
    https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html

    TODO returns a generator so rename to get_edges_by_attribute or make this return the first instance?
    If the attribute_field does not exist for a particular edge then it is ignored
    Edges can have different attribute dicts
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


def get_all_complex_paths(net, node_list):
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


def get_all_paths_from_nodes(net, node_list, with_direction=False):
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
                edges = get_edges_from_node_pair(net, sn, en)
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
                    if with_direction:
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


def get_edges_from_node_pair(net, start_node, end_node):
    """
    Get all edges between two nodes

    This function can return multiple edges when there is more than
    one edge between two nodes
    """

    try:
        edges = net[start_node][end_node]
    except KeyError:
        if start_node != end_node:  # do not warn when checking for loops
            log.debug("Could not find edge (%s, %s)", start_node, end_node)
        edges = None

    return edges


def get_edges_from_nodes(
    net, node_list, with_direction=False, length_field=LENGTH_FIELD, return_unique=True
):
    """
    From a list of nodes, create pairs and then get the shortest edge between the two nodes
    Set with_direction to add a new attribute to the edge to show if it is matching the
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

            if with_direction:
                add_direction_flag(**edge._asdict())  # unpack namedtuple to **kwargs

            edge_list.append(edge)

    if return_unique:
        return list({v.key: v for v in edge_list}.values())
    else:
        return edge_list


def get_shortest_edge(edges, length_field=LENGTH_FIELD):
    """
    From a dictionary of edges, get the shortest edge
    by its length
    """

    if not edges:
        raise ValueError("The edge list is empty")
    return min(
        edges.items(), key=lambda x: x[1][length_field]
    )  # py3 can add default=None


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
        if has_loop(net):
            log.debug("The network is a loop")
            # return arbitrary node in this case
            unattached_node = start_node
        else:
            log.debug("Both ends of the edge are attached")
            unattached_node = None

    return unattached_node


def has_loop(net):
    """
    Check if the network is a loop
    """

    try:
        networkx.algorithms.cycles.find_cycle(net)
        return True
    except networkx.exception.NetworkXNoCycle:
        return False


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
        nodes: (list):  a list of network nodes e.g. [(224966, 437657), (225195, 437940)]

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
