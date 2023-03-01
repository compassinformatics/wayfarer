from wayfarer import loops, Edge
import logging
from tests import networks


def test_get_root_node():

    outdeg = [(0, 2), (1, 3), (2, 2)]
    root_node = loops.get_root_node(outdeg)
    assert root_node == 1

    outdeg = [(0, 2), (1, 2), (2, 2)]
    root_node = loops.get_root_node(outdeg)
    assert root_node == 0


def test_get_unique_lists():

    all_lists = [[1, 2, 3], [1, 3, 2]]
    unique_lists = loops.get_unique_lists(all_lists)
    assert unique_lists == [[1, 2, 3]]

    all_lists = [[1, 2, 3], [1, 3, 2, 4], [1, 3, 2]]
    unique_lists = loops.get_unique_lists(all_lists)
    assert unique_lists == [[1, 2, 3], [1, 3, 2, 4]]

    all_lists = [[1, 2], [2, 1], [1, 2]]
    unique_lists = loops.get_unique_lists(all_lists)
    assert unique_lists == [[1, 2]]


def test_get_loop_nodes():

    edges = [Edge(0, 1, "A", {}), Edge(1, 2, "B", {}), Edge(2, 0, "C", {})]
    loop_nodes = loops.get_loop_nodes(edges)
    assert loop_nodes == {0: [0, 1, 2]}


def test_is_loop():

    assert loops.is_loop(networks.circle_network()) is True


def test_is_not_loop():

    assert loops.is_loop(networks.triple_loop_network()) is False


def test_doctest():
    import doctest

    print(doctest.testmod(loops))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_get_unique_lists()
    # test_get_root_node()
    # test_get_loop_nodes()
    # test_is_loop()
    test_is_not_loop()
    print("Done!")
