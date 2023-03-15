"""
pytest -v tests/test_splitting.py
"""
import logging
import pytest
from wayfarer import routing, splitter, Edge, WITH_DIRECTION_FIELD
from wayfarer.splitter import SPLIT_KEY_SEPARATOR
from tests import networks
from networkx import NetworkXNoPath, NodeNotFound


def test_solve_all_simple_paths():

    net = networks.simple_network()
    simple_paths = routing.solve_all_simple_paths(net, 1, 5)
    assert list(simple_paths) == [[1, 2, 3, 4, 5]]


def test_solve_all_simple_paths_no_node():

    net = networks.simple_network()
    with pytest.raises(NodeNotFound):
        routing.solve_all_simple_paths(net, 1, 99)


def test_solve_all_simple_paths_cutoff():

    net = networks.simple_network()
    simple_paths = routing.solve_all_simple_paths(net, 1, 5, cutoff=3)
    assert list(simple_paths) == []

    net = networks.simple_network()
    simple_paths = routing.solve_all_simple_paths(net, 1, 3, cutoff=3)
    assert list(simple_paths) == [[1, 2, 3]]


def test_solve_all_shortest_paths():

    net = networks.circle_network()
    all_paths = routing.solve_all_shortest_paths(net, 1, 3)
    # print(list(all_paths))
    assert list(all_paths) == [[1, 2, 3], [1, 4, 3]]


def test_solve_all_shortest_paths_no_node():

    net = networks.circle_network()
    # it seems NetworkXNoPath is raised rather than NodeNotFound
    # when using all_shortest_paths in networkx
    # and it is only raised when the generator is turned into a list
    with pytest.raises(NetworkXNoPath):
        print(list(routing.solve_all_shortest_paths(net, 1, 99)))


def test_get_path_ends():

    edges = [Edge(0, 1, 1, {}), Edge(1, 2, 1, {})]
    ends = routing.get_path_ends(edges)
    # print(ends)
    assert ends == (0, 2)


def test_get_path_ends_single_edge():

    edges = [Edge(0, 1, 1, {})]
    ends = routing.get_path_ends(edges)
    # print(ends)
    assert ends == (0, 1)


def test_solve_shortest_path():

    net = networks.simple_network()
    edges = routing.solve_shortest_path(net, start_node=1, end_node=5)
    edge_ids = [edge.key for edge in edges]
    assert edge_ids == [1, 2, 3, 4]


def test_solve_shortest_path_directions():

    net = networks.simple_network()
    edges = routing.solve_shortest_path(net, start_node=1, end_node=5)

    edge_directions = [edge.attributes[WITH_DIRECTION_FIELD] for edge in edges]
    assert edge_directions == [True, True, True, True]

    edges = routing.solve_shortest_path(net, start_node=5, end_node=1)

    edge_directions = [edge.attributes[WITH_DIRECTION_FIELD] for edge in edges]
    assert edge_directions == [False, False, False, False]


def test_solve_shortest_path_split_network():

    net = networks.simple_network()

    splitter.split_network_edge(net, 3, [2, 8])
    edges = routing.solve_shortest_path(net, start_node=1, end_node=5)

    # for edge in edges:
    #    print(edge)

    edge_ids = [edge.key for edge in edges]
    # print(edge_ids)
    assert edge_ids == [
        1,
        2,
        f"3{SPLIT_KEY_SEPARATOR}2",
        f"3{SPLIT_KEY_SEPARATOR}8",
        f"3{SPLIT_KEY_SEPARATOR}10",
        4,
    ]


def test_doctest():
    import doctest

    print(doctest.testmod(routing))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_doctest()
    # test_solve_all_simple_paths_no_node()
    # test_solve_all_simple_paths_cutoff()
    # test_solve_all_shortest_paths()
    # test_solve_all_shortest_paths_no_node()
    # test_get_path_ends()
    # test_get_path_ends_single_edge()
    # test_solve_shortest_path_directions()
    test_solve_shortest_path_split_network()
    print("Done!")
