import logging
import itertools
import networkx
from wayfarer import functions, LENGTH_FIELD, Edge
from networkx.algorithms import eulerian_path


log = logging.getLogger("wayfarer")


def solve_shortest_path(
    net, start_node, end_node, with_direction: bool = True, weight: str = LENGTH_FIELD
):
    """
    Solve the shortest path between two nodes, returning a list of Edge objects
    """
    nodes = solve_shortest_path_from_nodes(net, [start_node, end_node], weight)
    return functions.get_edges_from_nodes(
        net, nodes, with_direction=with_direction, length_field=weight
    )


def solve_shortest_path_from_nodes(net, node_list, weight: str = LENGTH_FIELD):
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


def solve_shortest_path_from_edges():
    pass


def solve_matching_path(
    net, start_node, end_node, distance: int = 0, cutoff: int = 10, include_key=None
):
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
            net, path_nodes, with_direction=True
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


def solve_matching_path_from_nodes(net, node_list, distance: (float | int)):
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
        path_nodes = solve_shortest_path(net, [n1, n2])
        path_edges = functions.get_edges_from_nodes(net, path_nodes)
        if path_edges:
            all_edges.append(path_edges)

    all_edges = itertools.chain(*all_edges)
    # get a unique list of edges based on key
    unique_edges = list({v.key: v for v in all_edges}.values())

    # TODO following will not work if there is a closed loop
    full_path = find_ordered_path(unique_edges)
    start_node, end_node = get_path_ends(full_path)

    return solve_matching_path(net, start_node, end_node, distance)


# def create_subnet(edges) -> networkx.MultiGraph:
#    """
#    Create a subnetwork from an edge list
#    """
#    subnet = networkx.MultiGraph()

#    for edge in edges:
#        subnet.add_edge(edge.start_node, edge.end_node, edge.key)

#    return subnet


def get_path_ends(edges):
    """
    For a list of connected edges find the end nodes
    TODO check if the edges form a loop
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


def solve_all_simple_paths(net, start_node, end_node, cutoff: int = 10) -> list:
    """
    A simple path does not have any repeated nodes
    Cut-off will limit how many nodes to search for
    Returns an iterator of a list of list of nodes
    [[0, 1, 3], [0, 2, 3], [0, 3]]
    See https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html

    net = networkx.MultiGraph()
    net.add_edge("A","B",1)
    net.add_edge("B","C",2)
    net.add_edge("C","B",3)
    net.add_edge("C","D",4)
    pths = networkx.all_simple_paths(net, source="A", target="D")

    print(list(pths)) # [['A', 'B', 'C', 'D'], ['A', 'B', 'C', 'D']]
    """

    all_shortest_paths = []

    log.debug("Solving from %s to %s", start_node, end_node)
    try:
        all_shortest_paths = networkx.all_simple_paths(
            net, source=start_node, target=end_node, cutoff=cutoff
        )
    except KeyError:
        raise

    return all_shortest_paths


def solve_all_shortest_paths(net, start_node, end_node):
    """
    Includes loops / repeated nodes
    Returns an iterator of a list of list of nodes
    [[0, 1, 3], [0, 2, 3], [0, 3]]
    See https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.all_shortest_paths.html

    net = networkx.MultiGraph()
    net.add_edge("A","B",1)
    net.add_edge("B","C",2)
    net.add_edge("C","B",3)
    net.add_edge("C","D",4)
    pths = networkx.all_shortest_paths(net, source="A", target="D")

    print(list(pths)) # [['A', 'B', 'C', 'D']]
    """

    all_shortest_paths = []

    log.debug("Solving from %s to %s", start_node, end_node)
    try:
        all_shortest_paths = networkx.all_shortest_paths(
            net, source=start_node, target=end_node
        )
    except KeyError:
        raise

    return all_shortest_paths


def find_ordered_path(edges: list[Edge], start_node=None, with_direction: bool = True):
    """
     Given a collection of randomly ordered connected edges, find the full
     path, covering all edges, from one end to the other.
     A start_node can be provided to return the edges in a specific direction.
     Uses the
    `Eulerian Path <https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.euler.eulerian_path.html>`_
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
            ordered_path = reversed(ordered_path)
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
        if with_direction:
            functions.add_direction_flag(p[0], p[1], edge.attributes)
        ordered_edges.append(edge)

    return ordered_edges


if __name__ == "__main__":
    pass
