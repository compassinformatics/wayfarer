"""
pytest -v tests/test_splitting.py
"""
import logging
import pytest
from wayfarer import routing
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


def test_doctest():
    import doctest

    print(doctest.testmod(routing))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_doctest()
    # test_solve_all_simple_paths_no_node()
    # test_solve_all_simple_paths_cutoff()
    # test_solve_all_shortest_paths()
    test_solve_all_shortest_paths_no_node()
    print("Done!")
