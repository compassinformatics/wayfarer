import logging
import itertools
import networkx
from wayfarer import functions, LENGTH_FIELD, Edge
from networkx.algorithms import eulerian_path
from networkx import NetworkXNoPath, NodeNotFound


class MultipleEnds(Exception):
    pass


log = logging.getLogger("wayfarer")


def solve_shortest_path(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    start_node: (str | int),
    end_node: (str | int),
    with_direction_flag: bool = True,
    weight: str = LENGTH_FIELD,
):
    """
    Solve the shortest path between two nodes, returning a list of Edge objects
    """
    nodes = solve_shortest_path_from_nodes(net, [start_node, end_node], weight)
    return functions.get_edges_from_nodes(
        net, nodes, with_direction_flag=with_direction_flag, length_field=weight
    )


def solve_shortest_path_from_nodes(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    node_list: list[int | str],
    weight: str = LENGTH_FIELD,
) -> list[int | str]:
    """
    Return a list of nodes found by solving from each node in node_list to
    the next
    """
    nodes_in_path = []

    for start_node, end_node in functions.pairwise(node_list):

        log.debug("Solving from %s to %s", start_node, end_node)

        if start_node == end_node:
            log.debug("Same start and end node used for path: {}".format(start_node))
        else:
            try:
                nodes_in_path += networkx.shortest_path(
                    net, source=start_node, target=end_node, weight=weight
                )
            except KeyError:
                raise

    return nodes_in_path


def solve_shortest_path_from_edges(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), edge_id_list: list[int | str]
):
    """
    Return a path routing from edge to edge, rather than
    from node to node
    """

    log.debug(f"Edge ids used for path solve: {edge_id_list}")

    # remove any duplicates
    edge_id_list = functions.get_unique_ordered_list(edge_id_list)

    edges = []
    previous_edge_nodes = []  # type: list[int | str]

    for edge_id in edge_id_list:
        edge = functions.get_edge_by_key(net, edge_id)

        end_nodes = [edge.start_node, edge.end_node]

        if previous_edge_nodes:
            node_list = previous_edge_nodes + end_nodes
        else:
            node_list = end_nodes

        # set the edge_id in the list to have a length of 0 to ensure it is
        # part of the route if there are alternative paths

        original_length = float(edge.attributes[LENGTH_FIELD])
        edge.attributes[LENGTH_FIELD] = 0
        log.debug(
            f"Updated edge id {edge_id} to have length 0 from {original_length:.2f}"
        )

        if edge.start_node == edge.end_node:
            # self-loop
            edges += functions.get_edges_from_nodes(net, end_nodes)
        else:
            try:
                nodes = solve_shortest_path_from_nodes(net, node_list)
            except NetworkXNoPath as ex:
                log.warning(f"No path found using node_list: {node_list}")
                log.warning(ex)
                raise

            edges += functions.get_edges_from_nodes(net, nodes)

            # reset original length - note not in original implementation
            # ensure this is only reset after get_edges_from_nodes has been called
            edge.attributes[LENGTH_FIELD] = original_length

        if sorted(previous_edge_nodes) == sorted(end_nodes):
            # a loop of two edges - get all edges between the nodes
            loop_edges = functions.get_edges_from_nodes(
                net, [edge.start_node, edge.end_node]
            )
            if loop_edges:
                edges += loop_edges

        previous_edge_nodes = end_nodes

    # edge ids are not unique at this step - due to the case with doubling-back see test_simple_reversed
    unique_edge_ids = functions.get_unique_ordered_list((e.key for e in edges))
    assert len(unique_edge_ids) <= len(edges)

    # the solve should have <= all edges clicked on
    assert len(edge_id_list) <= len(unique_edge_ids)
    # all edges the user clicked on should be returned in the solve
    try:
        assert set(edge_id_list).issubset(unique_edge_ids)
    except AssertionError:
        # this can occur where there are 2 edges looping on to the same node
        # see test_dual_path
        log.debug(f"edge_id_list: {edge_id_list} unique_edge_ids: {unique_edge_ids}")
        raise

    solved_edges = []

    for edge_id in unique_edge_ids:
        edge = [e for e in edges if e.key == edge_id][
            0
        ]  # get the first edge from full list of edges
        solved_edges.append(edge)

    # start_key = edge_id_list[0]
    # start_edge = functions.get_edge_by_key(net, start_key)
    # start_node = start_edge.start_node

    return find_ordered_path(solved_edges, start_node=None)


def solve_matching_path(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    start_node: (str | int),
    end_node: (str | int),
    distance: int = 0,
    cutoff: int = 10,
    include_key: (str | int | None) = None,
) -> (list[Edge] | None):
    """
    Return the path between the nodes that best matches the
    distance
    If no distance is supplied the shortest path is returned

    Cut-off is the maximum number of edges to search for
    If long solves are not as expected then increase this value

    include_key can be used to only include paths that contain this edge key
    """

    paths = []

    all_shortest_paths = list(solve_all_simple_paths(net, start_node, end_node, cutoff))

    # check for self-loops if start and end nodes are the same
    if start_node == end_node:
        all_shortest_paths.append([start_node])

    for path_nodes in all_shortest_paths:

        all_paths = functions.get_all_paths_from_nodes(
            net, path_nodes, with_direction_flag=True
        )

        for path_edges in all_paths:

            if include_key and include_key not in [e.key for e in path_edges]:
                continue
            path_length = functions.get_path_length(path_edges)
            length_difference = abs(path_length - distance)
            log.debug([p.key for p in path_edges])
            log.debug(
                "Desired length: {} Solved path length: {} Difference: {}".format(
                    distance, path_length, length_difference
                )
            )
            paths.append((length_difference, path_edges, path_length))

    # take the closest matching path to the original length based on absolute difference

    if paths:
        edges = min(paths)[
            1
        ]  # min in list based on first tuple value (length_difference)
        log.debug("Desired and solved length difference: {}".format(min(paths)[0]))
    else:
        log.warning("No paths found")
        edges = None

    return edges


def solve_matching_path_from_nodes(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    node_list: list[int | str],
    distance: int,
) -> (list[Edge] | None):
    """
    From a list of unordered nodes find the longest path that connects all nodes
    Then rerun the solve from the start to the end of the path getting a path
    closest to the desired distance
    """

    if not node_list:
        return None

    # solve all paths from each node to all other nodes in the list
    all_edges = []

    # get unique combinations of node pairs

    # l = [1,2,3]
    # list(itertools.combinations(l, 2))
    # [(1, 2), (1, 3), (2, 3)]

    all_node_combinations = itertools.combinations(node_list, 2)

    for n1, n2 in all_node_combinations:
        path_nodes = solve_shortest_path(net, start_node=n1, end_node=n2)
        path_edges = functions.get_edges_from_nodes(net, path_nodes)
        if path_edges:
            all_edges.append(path_edges)

    all_edges_generator = itertools.chain(*all_edges)
    # get a unique list of edges based on key
    unique_edges = list({v.key: v for v in all_edges_generator}.values())

    # TODO following will not work if there is a closed loop
    full_path = find_ordered_path(unique_edges)
    start_node, end_node = get_path_ends(full_path)

    return solve_matching_path(net, start_node, end_node, distance)


def get_path_ends(edges: list[Edge]) -> tuple[(int | str), (int | str)]:
    """
    For a list of connected edges find the (unattached) end nodes
    TODO Check if the edges form a loop

    >>> edges = [Edge(0, 1, 1, {}), Edge(1, 2, 1, {})]
    >>> get_path_ends(edges)
    (0, 2)
    """

    # first check the case where there is only a single edge
    if len(edges) == 1:
        single_edge = edges[0]
        return single_edge.start_node, single_edge.end_node

    subnet = functions.edges_to_graph(edges)

    start_edge = edges[0]
    end_edge = edges[-1]

    start_node = functions.get_unattached_node(subnet, start_edge)
    end_node = functions.get_unattached_node(subnet, end_edge)

    return start_node, end_node


def solve_all_simple_paths(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    start_node: (int | str),
    end_node: (int | str),
    cutoff: int = 10,
) -> list:
    """
    Find all simple paths between the two nodes on the network.
    A simple path does not have any repeated nodes
    A wrapper function for `all_simple_paths <
    https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html>`_
    TODO add ``has_path`` check prior to running

    Args:
        net: The network
        start_node: The node Id of the start node
        end_node: The node Id of the end node
        cutoff: The maximum number of edges to search for before stopping the search
    Returns:
        An iterator of a list of list of nodes

    >>> edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {"LEN_": 10}), Edge(2, 1, "C", {"LEN_": 10})]
    >>> net = functions.edges_to_graph(edges)
    >>> pths = solve_all_simple_paths(net, 0, 2)
    >>> print(list(pths))
    [[0, 1, 2], [0, 1, 2]]
    """

    all_shortest_paths = []

    log.debug("Solving from %s to %s", start_node, end_node)
    try:
        all_shortest_paths = networkx.all_simple_paths(
            net, source=start_node, target=end_node, cutoff=cutoff
        )
    except NodeNotFound as ex:
        log.error(ex)  # target node 99 not in graph
        raise

    return all_shortest_paths


def solve_all_shortest_paths(
    net: (networkx.MultiGraph | networkx.MultiDiGraph),
    start_node: (int | str),
    end_node: (int | str),
):
    """
    Find all shortest paths between the two nodes on the network.
    This includes loops and repeated nodes.
    A wrapper function for `all_shortest_paths <
    https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.all_shortest_paths.html>`_
    Unsure why less results are returned in the example below than when using all_simple_paths

    Args:
        net: The network
        start_node: The node Id of the start node
        end_node: The node Id of the end node
    Returns:
        An iterator of a list of list of nodes

    >>> edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {"LEN_": 10}), Edge(2, 1, "C", {"LEN_": 10})]
    >>> net = functions.edges_to_graph(edges)
    >>> pths = solve_all_shortest_paths(net, 0, 2)
    >>> print(list(pths))
    [[0, 1, 2]]
    """

    all_shortest_paths = []

    log.debug("Solving from %s to %s", start_node, end_node)
    try:
        all_shortest_paths = networkx.all_shortest_paths(
            net, source=start_node, target=end_node
        )
    except Exception as ex:
        log.error(ex)  # errors only seem to be raised when the iterator is used
        raise

    return all_shortest_paths


def find_ordered_path(
    edges: list[Edge],
    start_node: (int | str | None) = None,
    with_direction_flag: bool = True,
) -> list[Edge]:
    """
     Given a collection of randomly ordered connected edges, find the full
     path, covering all edges, from one end to the other.
     A start_node can be provided to return the edges in a specific direction.
     Uses the
    `eulerian_path <https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.euler.eulerian_path.html>`_
    function from networkx
    """

    subnet = functions.edges_to_graph(edges)

    try:
        ordered_path = list(eulerian_path(subnet, source=None, keys=True))
    except networkx.exception.NetworkXError as ex:
        log.exception(ex)
        raise

    if len(ordered_path) == 0:
        raise (ValueError("No path found for the edges. Are they connected?"))

    ordered_edges = []

    # ensure the returned path follows the direction based on the start_node to end_node
    # if a start_node is provided

    if start_node:
        end_edge = ordered_path[-1]
        end_nodes = [end_edge[0], end_edge[1]]
        if start_node in end_nodes:
            ordered_path = list(reversed(ordered_path))
        else:
            start_edge = ordered_path[0]
            start_nodes = [start_edge[0], start_edge[1]]
            if start_node not in start_nodes:
                raise ValueError(
                    "The provided start_node {} was not found at the start or end of the path".format(
                        start_node
                    )
                )

    # now get the edge objects back from the edge list

    for p in ordered_path:
        edge_key = p[2]
        edge = next(e for e in edges if e.key == edge_key)
        if with_direction_flag:
            functions.add_direction_flag(p[0], p[1], edge.attributes)
        ordered_edges.append(edge)

    return ordered_edges


# if __name__ == "__main__":
#    import doctest
#    doctest.testmod()
