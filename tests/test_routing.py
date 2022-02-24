"""
pytest -v tests/test_routing.py
"""

import logging
from wayfarer import Edge, routing


def test_get_path_ends():

    edges = [
        Edge(0, 1, key="A", attributes={"EDGE_ID": "A", "LEN_": 100}),
        Edge(1, 2, key="B", attributes={"EDGE_ID": "B", "LEN_": 100}),
        Edge(2, 3, key="C", attributes={"EDGE_ID": "C", "LEN_": 100}),
    ]

    ordered_edges = routing.find_ordered_path(edges)
    start_node, end_node = routing.get_path_ends(ordered_edges)
    assert sorted((start_node, end_node)) == sorted((0, 3))

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

    ordered_edges = routing.find_ordered_path(edges)
    start_node, end_node = routing.get_path_ends(ordered_edges)
    assert sorted((start_node, end_node)) == sorted((0, 3))


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

    ordered_edges = routing.find_ordered_path(edges)
    start_node, end_node = routing.get_path_ends(ordered_edges)
    print((start_node, end_node))
    assert sorted((start_node, end_node)) == sorted((0, 3))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_get_path_ends3()
    print("Done!")
