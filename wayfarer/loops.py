"""
Module containing functions relating to loops
"""
import networkx
from networkx import cycles
from wayfarer import Edge, functions
import logging
from typing import Iterable


log = logging.getLogger("wayfarer")


def is_loop(net: (networkx.MultiGraph | networkx.MultiDiGraph)) -> bool:
    """
    Check if the entire network is a loop
    """

    try:
        edges = networkx.algorithms.cycles.find_cycle(net)
        if len(edges) == len(net.edges()):
            return True
        else:
            return False
    except networkx.exception.NetworkXNoCycle:
        return False


def has_loop(net: (networkx.MultiGraph | networkx.MultiDiGraph)) -> bool:
    """
    Check if the network has a loop
    """

    try:
        networkx.algorithms.cycles.find_cycle(net)
        return True
    except networkx.exception.NetworkXNoCycle:
        return False


def get_unique_lists(all_lists: Iterable) -> list:
    """
    Returns a unique list of lists, and preserves order

    >>> get_unique_lists([[1,2],[2,1],[1,2]])
    [[1, 2]]
    """
    unique_sorted_lists = []
    unique_lists = []

    for sublist in all_lists:
        if sorted(sublist) not in unique_sorted_lists:
            unique_sorted_lists.append(sorted(sublist))
            unique_lists.append(sublist)

    return unique_lists


def get_root_node(outdeg: list[tuple]) -> int | str:
    """
    Find the most connected node - this will be where a loop starts and ends
    If degrees are equal the first node will always be returned

    >>> outdeg = [(0, 2), (1, 3), (2, 2)]
    >>> get_root_node(outdeg)
    1
    """
    root_node = max(outdeg, key=lambda n: n[1])[
        0
    ]  # get the id of the node with the highest degree
    return root_node


def get_loop_nodes(edges: list[Edge]) -> dict:
    """
    Return a dict of nodes in a loop, with the key as the start node of the loop
    The order of the nodes in the list is sorted by node key, otherwise this is nondeterministic
    If an edge starts and ends at the same node it is not included as a loop here

    >>> edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {}), Edge(2, 0, "C", {})]
    >>> get_loop_nodes(edges)
    {0: [0, 1, 2]}
    """

    net = functions.edges_to_graph(edges)

    # to_directed adds two directed edges between each node
    loops = (
        loop for loop in cycles.simple_cycles(net.to_directed()) if len(loop) > 2
    )  # filter out any loops between 2 connected edges

    unique_loops = get_unique_lists(loops)
    if len(unique_loops) > 0:
        log.debug(("Unique loops", unique_loops))

    loop_nodes = {}

    for node_list in unique_loops:
        outdeg = net.degree(node_list)
        root_node = get_root_node(outdeg)
        loop_nodes[root_node] = sorted(node_list)

    return loop_nodes


def find_self_loop(
    net: (networkx.MultiGraph | networkx.MultiDiGraph), node_id: (str | int)
):
    """
    For a node_id check to see if any edges start
    and end at this node
    """
    return functions.get_edges_from_nodes(
        net, [node_id, node_id], with_direction_flag=True
    )
