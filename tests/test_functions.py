"""
pytest -v tests/test_functions.py
"""

import logging
import pytest
import wayfarer
from wayfarer import loader, functions, Edge, WITH_DIRECTION_FIELD
import networkx


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_get_edge_by_key(use_reverse_lookup):
    recs = [{"EDGE_ID": 1, "LEN_": 100, "NODEID_FROM": 0, "NODEID_TO": 100}]
    net = loader.load_network_from_records(recs, use_reverse_lookup=use_reverse_lookup)

    # print(net.graph.keys())
    if use_reverse_lookup:
        assert "keys" in net.graph.keys()  # dict_keys(['name', 'keys'])

    edge = functions.get_edge_by_key(net, 1, with_data=False)

    assert edge == (0, 100, 1, {})

    edge = functions.get_edge_by_key(net, 1, with_data=True)

    assert edge == (
        0,
        100,
        1,
        {"NODEID_FROM": 0, "LEN_": 100, "EDGE_ID": 1, "NODEID_TO": 100},
    )


def test_get_edge_by_key_missing():
    recs = [{"EDGE_ID": 1, "LEN_": 100, "NODEID_FROM": 0, "NODEID_TO": 100}]
    net = loader.load_network_from_records(recs)

    with pytest.raises(KeyError):
        functions.get_edge_by_key(net, -1)


def test_to_edge():
    edge = wayfarer.to_edge((0, 1, 1, {"LEN_": 10}))
    assert edge == Edge(start_node=0, end_node=1, key=1, attributes={"LEN_": 10})


def test_to_edge_no_attributes():
    """
    If no attributes are supplied in a tuple then an empty dict is returned
    """

    edge = wayfarer.to_edge((0, 1, 1))
    assert edge == Edge(start_node=0, end_node=1, key=1, attributes={})


def test_get_multiple_edges_by_attribute():
    net = networkx.MultiGraph()

    net.add_edge(0, 0, key=1, **{"EDGE_ID": 1, "LEN_": 100})
    net.add_edge(0, 0, key=2, **{"EDGE_ID": 1, "LEN_": 100})

    edges = list(functions.get_edges_by_attribute(net, "EDGE_ID", 1))
    assert edges == [
        (0, 0, 1, {"EDGE_ID": 1, "LEN_": 100}),
        (0, 0, 2, {"EDGE_ID": 1, "LEN_": 100}),
    ]


def test_get_single_path_from_nodes():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key=1, **{"EDGE_ID": 1, "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1])
    key_list = [[e.key for e in p] for p in paths]
    assert key_list == [[1]]


def test_get_all_paths_from_nodes():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key=1, **{"EDGE_ID": 1, "LEN_": 100})
    net.add_edge(1, 2, key=2, **{"EDGE_ID": 2, "LEN_": 100})
    net.add_edge(2, 3, key=3, **{"EDGE_ID": 3, "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1, 2, 3])
    key_list = [[e.key for e in p] for p in paths]
    assert key_list == [[1, 2, 3]]


def test_get_all_paths_from_nodes_with_direction():
    net = networkx.MultiGraph()

    net.add_edge(
        0, 1, key=1, **{"EDGE_ID": 1, "LEN_": 100, "NODEID_FROM": 0, "NODEID_TO": 1}
    )
    # add a reversed edge in the middle of the path
    net.add_edge(
        1, 2, key=2, **{"EDGE_ID": 2, "LEN_": 100, "NODEID_FROM": 2, "NODEID_TO": 1}
    )
    net.add_edge(
        2, 3, key=3, **{"EDGE_ID": 3, "LEN_": 100, "NODEID_FROM": 2, "NODEID_TO": 3}
    )

    paths = list(
        functions.get_all_paths_from_nodes(net, [0, 1, 2, 3], with_direction_flag=True)
    )
    path = paths[0]

    key_list = [e.key for e in path]
    assert key_list == [1, 2, 3]
    assert path[0].attributes["WITH_DIRECTION"] is True
    assert path[1].attributes["WITH_DIRECTION"] is False
    assert path[2].attributes["WITH_DIRECTION"] is True


def test_get_all_complex_paths():
    """
    D- shape
    """
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A")
    net.add_edge(1, 1, key="B")  # self-loop

    node_list = [0, 1]
    paths = functions.get_all_complex_paths(net, node_list)
    assert paths == [[0, 1], [0, 1, 1]]


def test_get_all_complex_paths2():
    """
    D-D shape
    """
    net = networkx.MultiGraph()

    net.add_edge(0, 0, key="A")
    net.add_edge(0, 1, key="B")
    net.add_edge(1, 1, key="C")

    node_list = [0, 1]
    paths = functions.get_all_complex_paths(net, node_list)
    assert paths == [[0, 1], [0, 0, 1], [0, 1, 1], [0, 0, 1, 1]]


def test_get_all_complex_paths3():
    """
    Self-loop in middle
    """
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A")
    net.add_edge(1, 2, key="B")
    net.add_edge(2, 2, key="C")
    net.add_edge(2, 3, key="D")

    node_list = [0, 1, 2, 3]
    paths = functions.get_all_complex_paths(net, node_list)
    assert paths == [[0, 1, 2, 3], [0, 1, 2, 2, 3]]


def test_get_all_paths_from_nodes_loop():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 1, key="B", **{"EDGE_ID": "B", "LEN_": 100})  # self-loop

    paths = functions.get_all_paths_from_nodes(net, [0, 1])
    key_list = [[e.key for e in p] for p in paths]
    assert key_list == [["A"], ["A", "B"]]


def test_get_all_paths_from_nodes_loop2():
    net = networkx.MultiGraph()

    net.add_edge(0, 0, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(0, 1, key="B", **{"EDGE_ID": "B", "LEN_": 100})
    net.add_edge(1, 1, key="C", **{"EDGE_ID": "C", "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1])
    key_list = [[e.key for e in p] for p in paths]
    print(key_list)
    assert key_list == [["B"], ["A", "B"], ["B", "C"], ["A", "B", "C"]]


def test_get_all_paths_from_nodes_loop3():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})
    net.add_edge(2, 2, key="C", **{"EDGE_ID": "C", "LEN_": 100})
    net.add_edge(2, 3, key="D", **{"EDGE_ID": "D", "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1, 2, 3])
    key_list = [[e.key for e in p] for p in paths]
    print(key_list)
    assert key_list == [["A", "B", "D"], ["A", "B", "C", "D"]]


def test_get_all_paths_from_nodes_loop4():
    # with parallel edge

    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})
    net.add_edge(2, 1, key="B2", **{"EDGE_ID": "B2", "LEN_": 100})  # parallel edge
    net.add_edge(2, 2, key="C", **{"EDGE_ID": "C", "LEN_": 100})  # self-loop
    net.add_edge(2, 3, key="D", **{"EDGE_ID": "D", "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1, 2, 3])
    key_list = [[e.key for e in p] for p in paths]

    assert key_list == [
        ["A", "B", "D"],
        ["A", "B2", "D"],
        ["A", "B", "C", "D"],
        ["A", "B2", "C", "D"],
    ]


def test_get_all_paths_from_nodes_roundabout():
    """
    Get both the full and broken paths of a roundabout
    """
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})
    net.add_edge(2, 3, key="C", **{"EDGE_ID": "C", "LEN_": 100})
    net.add_edge(3, 0, key="D", **{"EDGE_ID": "D", "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1, 2, 3])
    key_list = [[e.key for e in p] for p in paths]
    assert key_list == [["A", "B", "C"], ["A", "B", "C", "D"]]


def test_get_all_paths_from_roundabout_with_loops():
    net = networkx.MultiGraph()

    net.add_edge(0, 0, key="AA", **{"EDGE_ID": "AA", "LEN_": 100})
    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})
    net.add_edge(2, 3, key="C", **{"EDGE_ID": "C", "LEN_": 100})
    net.add_edge(3, 0, key="D", **{"EDGE_ID": "D", "LEN_": 100})

    paths = functions.get_all_paths_from_nodes(net, [0, 1, 2, 3])
    key_list = [[e.key for e in p] for p in paths]
    assert key_list == [
        ["A", "B", "C"],
        ["AA", "A", "B", "C"],
        ["A", "B", "C", "D"],
        ["AA", "A", "B", "C", "D"],
    ]


def test_get_unattached_node():
    net = networkx.MultiGraph()
    edge1 = (0, 1)
    edge2 = (1, 2)

    net.add_edge(*edge1)
    net.add_edge(*edge2)

    n = functions.get_unattached_node(net, edge1)
    assert n == 0

    n = functions.get_unattached_node(net, edge2)
    assert n == 2


def test_get_unattached_node2():
    net = networkx.MultiGraph()
    edge1 = (0, 1)
    edge2 = (1, 2)
    edge3 = (2, 3)

    net.add_edge(*edge1)
    net.add_edge(*edge2)
    net.add_edge(*edge3)

    n = functions.get_unattached_node(net, edge1)
    assert n == 0

    n = functions.get_unattached_node(net, edge2)
    assert n is None

    n = functions.get_unattached_node(net, edge3)
    assert n == 3


def test_get_multiconnected_nodes():
    edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {})]
    nodes = functions.get_multiconnected_nodes(edges, connections=2)
    assert nodes == [1]


def test_get_ordered_end_nodes():
    edges = [Edge(1, 2, "A", {}), Edge(0, 1, "B", {})]
    nodes = [0, 1]
    end_nodes = functions.get_ordered_end_nodes(edges, nodes)
    assert end_nodes == [1, 0]


def test_get_edges_from_nodes():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(
        1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100, "NODEID_FROM": 1, "NODEID_TO": 2}
    )
    net.add_edge(2, 3, key="C", **{"EDGE_ID": "C", "LEN_": 100})

    node_list = [1, 2]
    edges = functions.get_edges_from_nodes(net, node_list)
    assert len(edges) == 1
    edges[0].key == "B"

    edges = functions.get_edges_from_nodes(net, [2, 1], with_direction_flag=True)
    assert len(edges) == 1
    assert edges[0].key == "B"
    assert edges[0].attributes[WITH_DIRECTION_FIELD] is False


def test_get_edges_from_nodes_non_unique():
    net = networkx.MultiGraph()

    net.add_edge(1, 2, key="A", **{"EDGE_ID": "A", "LEN_": 100})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})

    node_list = [1, 2, 1]
    edges = functions.get_edges_from_nodes(net, node_list, return_unique=True)
    assert len(edges) == 1
    edges[0].key == "B"

    edges = functions.get_edges_from_nodes(net, node_list, return_unique=False)
    assert len(edges) == 2
    edges[0].key == "B"
    edges[1].key == "B"


def test_edges_to_graph():
    edges = []
    net = functions.edges_to_graph(edges)
    assert len(net.edges()) == 0

    edges = [Edge(0, 1, key=1, attributes={}), Edge(1, 2, key=2, attributes={})]
    net = functions.edges_to_graph(edges)
    assert len(net.edges()) == 2
    assert list(net.edges(keys=True)) == [(0, 1, 1), (1, 2, 2)]


def test_edges_to_graph_no_keys():
    tuples = [(0, 1), (1, 2)]
    net = functions.edges_to_graph(tuples)
    assert len(net.edges()) == 2
    # when no keys are set networkx uses 0 for all keys
    assert list(net.edges(keys=True)) == [(0, 1, 0), (1, 2, 0)]


def test_get_shortest_edge():
    edges = {
        "A": {"EDGE_ID": "A", "LEN_": 100, "NODEID_FROM": 1, "NODEID_TO": 2},
        "B": {"EDGE_ID": "B", "LEN_": 20, "NODEID_FROM": 2, "NODEID_TO": 3},
    }
    res = functions.get_shortest_edge(edges)
    assert res[0] == "B"


def test_get_shortest_edge_identical():
    """
    If two edges have identical lengths always
    return whichever key is first in the dict
    """
    edges = {
        1: {"EDGE_ID": 1, "LEN_": 100},
        -1: {"EDGE_ID": 2, "LEN_": 100},
    }
    res = functions.get_shortest_edge(edges)
    assert res[0] == 1


def test_get_shortest_edge_mixed_keys():
    edges = {
        1: {"EDGE_ID": "A", "LEN_": 100, "NODEID_FROM": 1, "NODEID_TO": 2},
        "A": {"EDGE_ID": "B", "LEN_": 20, "NODEID_FROM": 2, "NODEID_TO": 3},
    }
    res = functions.get_shortest_edge(edges)
    assert res[0] == "A"


def test_get_unique_ordered_list():
    lst = [2, 2, 1, 1, 4, 4, 1, 2, 3]
    res = functions.get_unique_ordered_list(lst)
    print(res)
    assert res == [2, 1, 4, 3]


def test_get_edges_from_node_pair():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key="A", val="foo")
    net.add_edge(0, 1, key="B", val="bar")

    tpls = functions.get_edges_from_node_pair(net, start_node=0, end_node=1)
    assert tpls == {"A": {"val": "foo"}, "B": {"val": "bar"}}


def test_get_path_length():
    edges = [Edge(0, 1, "A", {"LEN_": 5}), Edge(1, 2, "B", {"LEN_": 5})]
    assert functions.get_path_length(edges) == 10


def test_has_overlaps():
    edges = [
        Edge(0, 1, "A", {"EDGE_ID": 1, "OFFSET": 0, "LEN_": 10}),
        Edge(1, 2, "B", {"EDGE_ID": 2, "OFFSET": 0, "LEN_": 10}),
        Edge(2, 3, "C", {"EDGE_ID": 3, "OFFSET": 0, "LEN_": 10}),
        Edge(2, 3, "C", {"EDGE_ID": 2, "OFFSET": 0, "LEN_": 10}),
        Edge(2, 3, "C", {"EDGE_ID": 4, "OFFSET": 0, "LEN_": 10}),
    ]
    assert functions.has_overlaps(edges) is True


def test_has_no_overlaps():
    edges = [
        Edge(0, 1, "A", {"EDGE_ID": 1}),
        Edge(1, 2, "B", {"EDGE_ID": 2}),
        Edge(2, 3, "C", {"EDGE_ID": 3}),
        Edge(2, 3, "C", {"EDGE_ID": 4}),
    ]
    assert functions.has_overlaps(edges) is False


def test_has_no_overlaps_loop():
    edges = [
        Edge(0, 1, "A", {"EDGE_ID": 1}),
        Edge(1, 2, "B", {"EDGE_ID": 2}),
        Edge(2, 3, "C", {"EDGE_ID": 3}),
        Edge(0, 1, "D", {"EDGE_ID": 1}),
    ]

    assert functions.has_overlaps(edges) is False


def test_has_no_overlaps_loop_with_split():
    edges = [
        Edge(0, 1, "A", {"EDGE_ID": 1, "OFFSET": 5, "LEN_": 10}),
        Edge(1, 2, "B", {"EDGE_ID": 2, "OFFSET": 0, "LEN_": 10}),
        Edge(1, 2, "B", {"EDGE_ID": 2, "OFFSET": 10, "LEN_": 10}),
        Edge(2, 3, "C", {"EDGE_ID": 3, "OFFSET": 0, "LEN_": 10}),
        Edge(3, 0, "C", {"EDGE_ID": 4, "OFFSET": 0, "LEN_": 5}),
    ]
    assert functions.has_overlaps(edges) is False


def test_doctest():
    import doctest

    print(doctest.testmod(functions))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_get_edges_from_nodes()
    # test_edges_to_graph()
    # test_get_edges_from_nodes()
    # test_edges_to_graph()
    # test_get_shortest_edge()
    # test_get_shortest_edge_identical()
    # test_get_shortest_edge_mixed_keys()
    # test_get_unique_ordered_list()
    # test_get_edges_from_node_pair()
    # test_to_edge()
    # test_to_edge_no_attributes()
    # test_edges_to_graph_no_keys()
    # test_get_edge_by_key_missing()
    # test_get_all_paths_from_nodes_with_direction()
    # test_get_path_length()
    # test_doctest()
    # test_get_edges_from_nodes_non_unique()
    # test_has_no_overlaps()
    # test_has_no_overlaps_loop()
    # test_has_overlaps()
    test_has_no_overlaps_loop_with_split()
    print("Done!")
