"""
A collection of functions to help validate a network
"""

from collections import Counter


def duplicate_keys(net):
    """
    Find any duplicate keys in the network
    Keys must be unique for routing to function correctly
    """

    keys = []

    for u, v, k in net.edges(keys=True):
        keys.append(k)

    duplicates = [item for item, count in Counter(keys).items() if count > 1]
    return duplicates


def valid_reverse_lookup(net):
    """
    Check if the reverse lookup dictionary
    has the same count as edges in the network
    """
    return len(net.graph["keys"]) == len(net.edges())


def recalculate_keys(net):
    """
    Recalculate keys in the reverse lookup dict
    These can become out-of-synch following a merge of networks e.g. with
    the compose_all function
    """

    net.graph["keys"] = {}
    for start_node, end_node, key in net.edges(keys=True):
        net.graph["keys"][key] = (start_node, end_node)


def edge_attributes(net, with_sample_data=False):
    """
    Return the list of attributes for the edges
    in the network
    """

    attributes_with_data = []
    attributes = []

    for u, v, d in net.edges(data=True):
        keys = sorted(d.keys())
        if keys not in attributes:
            attributes.append(keys)
            if with_sample_data:
                attributes_with_data.append(d)

    if with_sample_data:
        return attributes_with_data
    else:
        return attributes
