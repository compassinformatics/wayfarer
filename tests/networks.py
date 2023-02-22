"""
This file contains a collection of various network forms
"""
from wayfarer import (
    EDGE_ID_FIELD,
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    loader,
)


def tuples_to_net(tuples):
    """
    Takes in a list of tuples in the form (1, 1, 2, 10) and
    converts to {'EDGE_ID': 1, 'NODEID_FROM': 1, 'NODEID_TO': 2, 'LEN_': 10}
    before adding to a network
    """

    fields = [EDGE_ID_FIELD, NODEID_FROM_FIELD, NODEID_TO_FIELD, LENGTH_FIELD]
    recs = [dict(zip(fields, t)) for t in tuples]
    # print(recs)
    return loader.load_network_from_records(recs)


def simple_network():
    """
    A simple network of connected edges from 1 to 5
    """

    data = [(1, 1, 2, 10), (2, 2, 3, 10), (3, 3, 4, 10), (4, 4, 5, 10)]
    return tuples_to_net(data)


def reverse_network():
    """
    Start and ends in different directions
    """

    data = [(1, 1, 2, 10), (2, 3, 1, 10), (3, 3, 5, 5), (4, 5, 4, 5)]
    return tuples_to_net(data)


def t_network():
    """
    Create a T shaped network
    """

    data = [(1, 1, 2, 10), (2, 2, 3, 10), (3, 3, 4, 10), (4, 3, 5, 10)]
    return tuples_to_net(data)


def single_edge_loop_network():
    """
    Create a network with a single edge loop at one end
    """

    data = [(1, 1, 2, 10), (2, 2, 3, 10), (3, 3, 3, 10)]
    return tuples_to_net(data)


def dual_path_network():
    """
    Network has 3 edges, 2 of which are between the same nodes
    Cannot make DOT file
    http://stackoverflow.com/questions/35007046/how-to-draw-parallel-edges-in-networkx-graphviz
    and image doesn't show both edges
    """

    data = [
        (1, 1, 2, 10),
        (2, 2, 3, 10),
        (3, 2, 3, 20),
    ]  # longer edge of 20 to create loop
    return tuples_to_net(data)


def p_network():
    """
    Network has 4 edges, the last of which loops back on itself
    """

    data = [(1, 1, 2, 10), (2, 2, 3, 10), (3, 3, 4, 5), (4, 4, 2, 5)]
    return tuples_to_net(data)


def loop_middle_network():
    """
    Network has a loop in the middle of the network
    """

    data = [(1, 1, 2, 10), (2, 2, 3, 10), (3, 3, 4, 5), (4, 4, 2, 5), (5, 2, 5, 5)]
    return tuples_to_net(data)


def double_loop_network():
    """
    Network has a loop at the start and end of the path
    """

    data = [
        (1, 1, 2, 10),
        (2, 2, 3, 10),
        (3, 3, 1, 5),
        (4, 1, 4, 5),
        (5, 4, 5, 5),
        (6, 5, 6, 5),
        (7, 6, 4, 5),
    ]
    return tuples_to_net(data)


def triple_loop_network():
    """
    Network has a loop in the middle of the network and at the start and end
    NOT SUPPORTED
    """

    data = [
        (1, 1, 2, 10),
        (2, 2, 3, 10),
        (3, 3, 1, 10),
        (4, 1, 4, 5),
        (5, 4, 5, 5),
        (6, 5, 6, 5),
        (7, 6, 4, 5),
        (8, 4, 7, 5),
        (9, 7, 8, 5),
        (10, 8, 9, 5),
        (11, 9, 7, 5),
    ]
    return tuples_to_net(data)


def circle_network():
    """
    Network in a circle
    """

    data = [
        (1, 1, 2, 5),
        (2, 2, 3, 5),
        (3, 3, 4, 10),
        (4, 4, 1, 10),
    ]
    return tuples_to_net(data)


def reversed_loop_network():

    data = [
        (1, 1, 2, 10),
        (2, 2, 5, 10),
        (3, 5, 4, 10),
        (4, 4, 99, 10),
        (5, 99, 2, 10),
    ]
    return tuples_to_net(data)


def bottle_network():
    """
    Create a bottle-shaped network
    For testing creating a specific "loop" segment (lollipop route)
    Same as dual_network above
    """

    data = [
        (1, 1, 2, 10),
        (2, 2, 3, 10),
        (3, 3, 2, 10),
    ]
    return tuples_to_net(data)


if __name__ == "__main__":
    simple_network()
    print("Done!")
