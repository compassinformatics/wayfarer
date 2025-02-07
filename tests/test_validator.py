"""
pytest -v tests/test_validator.py
"""

from wayfarer import loader, validator
import networkx


def create_net_with_duplicates():
    net = networkx.MultiGraph()

    networkx.add_path(net, [0, 1, 2])
    net.add_edge(2, 3, key=1, **{"EDGE_ID": 1, "LEN_": 100})
    net.add_edge(3, 4, key="C", **{"EDGE_ID": 1, "LEN_": 100})
    net.add_edge(4, 5, key="C", **{"EDGE_ID": 1, "LEN_": 100})

    return net


def create_net_without_duplicates():
    net = networkx.MultiGraph()

    net.add_edge(0, 1, key=0)
    net.add_edge(1, 2, key=1)
    net.add_edge(2, 3, key=3)

    return net


def test_duplicate_keys():
    net_with_duplicates = create_net_with_duplicates()
    net_without_duplicates = create_net_without_duplicates()

    duplicates = validator.duplicate_keys(net_with_duplicates)
    no_duplicates = validator.duplicate_keys(net_without_duplicates)

    assert duplicates == [0, "C"] and no_duplicates == []


def test_valid_reverse_lookup():
    recs = [
        {"EDGE_ID": "A", "LEN_": 100, "NODEID_FROM": 0, "NODEID_TO": 100},
        {"EDGE_ID": "B", "LEN_": 100, "NODEID_FROM": 100, "NODEID_TO": 200},
    ]
    net = loader.load_network_from_records(recs, use_reverse_lookup=True)

    assert validator.valid_reverse_lookup(net)


def test_recalculate_keys():
    recs1 = [
        {"EDGE_ID": "A", "LEN_": 100, "NODEID_FROM": 0, "NODEID_TO": 100},
        {"EDGE_ID": 1, "LEN_": 100, "NODEID_FROM": 100, "NODEID_TO": 200},
    ]
    net1 = loader.load_network_from_records(recs1, use_reverse_lookup=True)

    recs2 = [
        {"EDGE_ID": "B", "LEN_": 100, "NODEID_FROM": 100, "NODEID_TO": 200},
        {"EDGE_ID": 2, "LEN_": 100, "NODEID_FROM": 200, "NODEID_TO": 300},
    ]
    net2 = loader.load_network_from_records(recs2, use_reverse_lookup=True)

    net = networkx.compose(net1, net2)

    validator.recalculate_keys(net)

    assert net.graph["keys"] == {
        "A": (0, 100),
        1: (100, 200),
        "B": (100, 200),
        2: (200, 300),
    }


def test_edge_attributes():
    recs = [{"EDGE_ID": 0, "LEN_": 10, "NODEID_FROM": 0, "NODEID_TO": 10, "PROP1": "A"}]
    net = loader.load_network_from_records(recs)

    attributes = validator.edge_attributes(net)

    assert attributes == [["EDGE_ID", "LEN_", "NODEID_FROM", "NODEID_TO", "PROP1"]]
