"""
pytest -v tests/test_routing_ordered_path.py
"""

import logging
import pytest
from wayfarer import Edge, routing, loops, functions
from tests import networks
import wayfarer
from networkx.exception import NetworkXError


def test_get_path_ends():

    edges = [
        Edge(0, 1, key="A", attributes={"EDGE_ID": "A", "LEN_": 100}),
        Edge(1, 2, key="B", attributes={"EDGE_ID": "B", "LEN_": 100}),
        Edge(2, 3, key="C", attributes={"EDGE_ID": "C", "LEN_": 100}),
    ]

    ordered_edges = routing.find_ordered_path(edges, with_direction_flag=False)
    start_node, end_node = routing.get_path_ends(ordered_edges)
    assert start_node == 0
    assert end_node == 3

    # assert 2, 0 == (2,4) # WARNING will always return True! As interpreted as assert (2, 0) # True


def test_get_path_ends2():
    """
    A P shape
    """

    edges = [
        Edge(0, 1, key="A", attributes={"EDGE_ID": "A", "LEN_": 100}),
        Edge(1, 2, key="B", attributes={"EDGE_ID": "B", "LEN_": 100}),
        Edge(2, 3, key="C", attributes={"EDGE_ID": "C", "LEN_": 100}),
        Edge(3, 1, key="D", attributes={"EDGE_ID": "D", "LEN_": 100}),
    ]

    ordered_edges = routing.find_ordered_path(edges, with_direction_flag=False)
    start_node, end_node = routing.get_path_ends(ordered_edges)

    assert start_node == 0
    assert end_node == 3


def test_get_path_ends3():
    """
    A P shape - inverse loop
    """

    edges = [
        Edge(0, 1, key="A", attributes={"EDGE_ID": "A", "LEN_": 100}),
        Edge(2, 1, key="B", attributes={"EDGE_ID": "B", "LEN_": 100}),
        Edge(3, 2, key="C", attributes={"EDGE_ID": "C", "LEN_": 100}),
        Edge(3, 1, key="D", attributes={"EDGE_ID": "D", "LEN_": 100}),
    ]

    ordered_edges = routing.find_ordered_path(edges, with_direction_flag=False)
    start_node, end_node = routing.get_path_ends(ordered_edges)

    assert start_node == 0
    assert end_node == 3


def test_simple_network():

    # simple case
    net = networks.simple_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loops.has_loop(net) is False
    loop_nodes = loops.get_loop_nodes(edges)
    # no loops
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1, 5]

    edges = routing.find_ordered_path(edges)
    edge_ids = [edge.key for edge in edges]
    assert edge_ids == [1, 2, 3, 4]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=5)
    edge_ids = [edge.key for edge in edges]
    assert edge_ids == [1, 2, 3, 4]

    edge_id_list = [1, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4]

    edge_id_list = [4, 1]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [4, 3, 2, 1]

    edge_id_list = [3, 4, 1]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [4, 3, 2, 1]


def test_single_edge_loop_network():

    net = networks.single_edge_loop_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # no loops (self-loops on one node are not included)
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1]

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=3)
    assert [edge.key for edge in edges] == [1, 2]

    edges = routing.solve_shortest_path(net, start_node=3, end_node=1)
    assert [edge.key for edge in edges] == [2, 1]

    edge_id_list = [3, 2]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [3, 2]

    edge_id_list = [2]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [2]

    # TOD this throw an error - Graph has no Eulerian path
    edge_id_list = [1, 3]
    # edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    # assert [e.key for e in edges] == [1, 2, 3]


def test_reverse_network():

    net = networks.reverse_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # no loops
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [2, 4]

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4]

    edges = routing.solve_shortest_path(net, start_node=4, end_node=2)
    assert [edge.key for edge in edges] == [4, 3, 2, 1]

    edge_id_list = [1, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4]

    edge_id_list = [4, 1]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [4, 3, 2, 1]

    edge_id_list = [3, 1, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4]


def test_t_network():

    # simple case
    net = networks.t_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # no loops
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1, 4, 5]

    with pytest.raises(NetworkXError):
        routing.find_ordered_path(edges)

    edges = routing.solve_shortest_path(net, start_node=1, end_node=4)
    assert [edge.key for edge in edges] == [1, 2, 3]

    # throw error
    with pytest.raises(NetworkXError):
        edge_id_list = [3, 1, 4]
        edges = routing.solve_shortest_path_from_edges(net, edge_id_list)


def test_p_network():

    # simple case
    net = networks.p_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    assert loop_nodes[2] == [2, 3, 4]

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1]

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=3)
    assert [edge.key for edge in edges] == [1, 2]

    edge_id_list = [1, 2, 3, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4]

    edge_id_list = [4, 3, 2, 1]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [4, 3, 2, 1]

    edge_id_list = [3, 1, 2, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    # print([e.key for e in edges])
    assert [e.key for e in edges] == [2, 3, 4, 1]


def test_double_loop_network():

    net = networks.double_loop_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # loops
    assert loop_nodes[1] == [1, 2, 3]
    assert loop_nodes[4] == [4, 5, 6]

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == []

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4, 5, 6, 7]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=6)
    assert [edge.key for edge in edges] == [4, 7]

    edge_id_list = [1, 2, 3, 4, 5, 6, 7]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4, 5, 6, 7]

    edge_id_list = [4, 3, 2, 1, 5, 7, 6]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [3, 2, 1, 4, 5, 6, 7]

    edge_id_list = [3, 1, 6, 2, 4, 5, 7]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    # print([e.key for e in edges])
    assert [e.key for e in edges] == [3, 2, 1, 4, 5, 6, 7]


def test_circle_network():

    net = networks.circle_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # loops
    assert loop_nodes[1] == [1, 2, 3, 4]

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == []

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=4)
    assert [edge.key for edge in edges] == [4]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=3)
    assert [edge.key for edge in edges] == [1, 2]

    edge_id_list = [1, 2, 3, 4]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3, 4]

    edge_id_list = [4, 3, 2, 1]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    # print([e.key for e in edges])
    # 4, 3, 2, 1 is equally valid, but the eulerian_path returns them in this order
    assert [e.key for e in edges] == [4, 1, 2, 3]

    edge_id_list = [2, 1, 4, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    # print([e.key for e in edges])
    # 2, 1, 4, 3 is equally valid, but the eulerian_path returns them in this order
    assert [e.key for e in edges] == [2, 3, 4, 1]


def test_dual_path():

    net = networks.dual_path_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # no loops (self-loops on one node are not included)
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1]

    edges = routing.find_ordered_path(edges)
    # print([e.key for e in edges])
    assert [edge.key for edge in edges] == [1, 2, 3]

    edge_id_list = [1, 2]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2]

    edge_id_list = [1, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 3]

    edge_id_list = [1, 2]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2]

    edge_id_list = [1, 2, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3]


def test_loop_middle_network():

    net = networks.loop_middle_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    assert loop_nodes[2] == [2, 3, 4]

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1, 5]

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4, 5]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=5)
    assert [edge.key for edge in edges] == [1, 5]

    edges = routing.solve_shortest_path(net, start_node=1, end_node=3)
    assert [edge.key for edge in edges] == [1, 2]

    edge_id_list = [1, 2, 3, 4, 5]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    print([e.key for e in edges])
    assert [e.key for e in edges] == [1, 2, 3, 4, 5]


def test_triple_loop_network():

    net = networks.triple_loop_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    assert loop_nodes[1] == [1, 2, 3]
    assert loop_nodes[4] == [4, 5, 6]
    assert loop_nodes[7] == [7, 8, 9]

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == []

    edges = routing.find_ordered_path(edges)
    assert [edge.key for edge in edges] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    edges = routing.solve_shortest_path(net, start_node=5, end_node=8)
    assert [edge.key for edge in edges] == [5, 8, 9]

    edge_id_list = [2, 8, 10]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [2, 3, 4, 8, 9, 10]


def test_bottle_network():

    net = networks.bottle_network()
    edges = wayfarer.to_edges(net.edges(keys=True, data=True))

    loop_nodes = loops.get_loop_nodes(edges)
    # no loops (self-loops on one node are not included)
    assert len(loop_nodes) == 0

    end_nodes = functions.get_end_nodes(edges)
    assert end_nodes == [1]

    edges = routing.find_ordered_path(edges)
    # print([e.key for e in edges])
    assert [edge.key for edge in edges] == [1, 2, 3]

    edge_id_list = [1, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 3]

    edge_id_list = [1, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 3]

    edge_id_list = [1, 2]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2]

    edge_id_list = [1, 2, 3]
    edges = routing.solve_shortest_path_from_edges(net, edge_id_list)
    assert [e.key for e in edges] == [1, 2, 3]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_get_path_ends()
    # test_get_path_ends2()
    # test_get_path_ends3()
    # test_simple_network()
    # test_single_edge_loop_network()
    # test_reverse_network()
    # test_t_network()
    # test_p_network()
    # test_double_loop_network()
    test_circle_network()
    # test_dual_path()
    # test_loop_middle_network()
    # test_triple_loop_network()
    # test_bottle_network()
    print("Done!")
