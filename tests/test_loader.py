import wayfarer
from wayfarer import loader, functions, Edge
import networkx
import pytest
import logging
import tempfile


def test_add_edge():

    net = networkx.MultiGraph()
    key = loader.add_edge(net, {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 1})
    assert key == 1


def test_add_edge_missing_key():

    net = networkx.MultiGraph()
    with pytest.raises(KeyError):
        loader.add_edge(net, {"XEDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 1})


def test_add_edge_with_reverse_lookup():

    reverse_lookup = loader.UniqueDict()
    net = networkx.MultiGraph(keys=reverse_lookup)
    key = loader.add_edge(net, {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 1})
    assert key == 1
    assert reverse_lookup[1] == (1, 1)


def test_create_graph():

    net = loader.create_graph()
    assert type(net) is networkx.classes.multigraph.MultiGraph
    version = wayfarer.__version__
    assert (
        str(net)
        == f"MultiGraph named 'Wayfarer Generated MultiGraph (version {version})' with 0 nodes and 0 edges"
    )
    assert net.graph["keys"] == {}


def test_create_multidigraph():

    net = loader.create_graph(graph_type=networkx.MultiDiGraph)
    assert type(net) is networkx.classes.multidigraph.MultiDiGraph
    version = wayfarer.__version__
    assert (
        str(net)
        == f"MultiDiGraph named 'Wayfarer Generated MultiDiGraph (version {version})' with 0 nodes and 0 edges"
    )


def test_create_graph_no_lookup():

    net = loader.create_graph(use_reverse_lookup=False)
    assert "keys" not in net.graph


def test_load_network_from_records():

    rec1 = {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 2, "LEN_": 5, "PROP1": "A"}
    rec2 = {"EDGE_ID": 2, "NODEID_FROM": 2, "NODEID_TO": 3, "LEN_": 15, "PROP1": "B"}
    recs = [rec1, rec2]

    net = loader.load_network_from_records(recs)
    assert net.graph["keys"] == {1: (1, 2), 2: (2, 3)}


def test_load_network_from_records_missing_key():

    rec1 = {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 2, "LEN_": 5, "PROP1": "A"}
    rec2 = {"XEDGE_ID": 2, "NODEID_FROM": 2, "NODEID_TO": 3, "LEN_": 15, "PROP1": "B"}
    recs = [rec1, rec2]

    with pytest.raises(KeyError):
        loader.load_network_from_records(recs)


def test_load_network_from_geometries():

    rec1 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]},
        "properties": {"EDGE_ID": 1, "LEN_": 1},
    }
    rec2 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 1), (0, 2)]},
        "properties": {"EDGE_ID": 2, "LEN_": 1},
    }
    recs = [rec1, rec2]

    net = loader.load_network_from_geometries(recs)
    assert net.graph["keys"] == {1: ("0|0", "0|1"), 2: ("0|1", "0|2")}

    edge = functions.get_edge_by_key(net, 2)
    assert edge == Edge(
        start_node="0|1",
        end_node="0|2",
        key=2,
        attributes={
            "EDGE_ID": 2,
            "LEN_": 1,
            "NODEID_FROM": "0|1",
            "NODEID_TO": "0|2",
        },
    )


def test_load_network_from_geometries_calculated_length():

    rec1 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]},
        "properties": {"EDGE_ID": 1},
    }
    rec2 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 1), (0, 2)]},
        "properties": {"EDGE_ID": 2},
    }
    recs = [rec1, rec2]

    net = loader.load_network_from_geometries(recs)
    assert net.graph["keys"] == {1: ("0|0", "0|1"), 2: ("0|1", "0|2")}

    edge = functions.get_edge_by_key(net, 2)
    assert edge == Edge(
        start_node="0|1",
        end_node="0|2",
        key=2,
        attributes={
            "EDGE_ID": 2,
            "LEN_": 1,
            "NODEID_FROM": "0|1",
            "NODEID_TO": "0|2",
        },
    )


def test_load_network_from_invalid_geometries():

    rec1 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]},
        "properties": {"EDGE_ID": 1},
    }
    rec2 = {
        "geometry": {"type": "MultiLineString", "coordinates": [[(0, 1), (0, 2)]]},
        "properties": {"EDGE_ID": 2},
    }
    recs = [rec1, rec2]

    with pytest.raises(ValueError):
        loader.load_network_from_geometries(recs)


def test_load_network_from_invalid_geometries_skip():

    rec1 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]},
        "properties": {"EDGE_ID": 1},
    }
    rec2 = {
        "geometry": {"type": "MultiLineString", "coordinates": [[(0, 1), (0, 2)]]},
        "properties": {"EDGE_ID": 2},
    }
    recs = [rec1, rec2]

    net = loader.load_network_from_geometries(recs, skip_errors=True)
    assert len(net.edges()) == 1


def test_load_network_from_invalid_geometries_missing_key():

    rec1 = {
        "geometry": {"type": "LineString", "coordinates": [(0, 0), (0, 1)]},
        "properties": {"MYKEY": 2},
    }

    recs = [rec1]

    with pytest.raises(KeyError):
        loader.load_network_from_geometries(recs)


def test_uniquedict():

    ud = loader.UniqueDict()
    ud[1] = "foo"
    ud[2] = "bar"

    assert ud == {1: "foo", 2: "bar"}


def test_uniquedict_error():

    ud = loader.UniqueDict()
    ud[1] = "foo"

    with pytest.raises(KeyError):
        ud[1] = "bar"


def test_pickling():

    net = loader.create_graph()
    loader.add_edge(net, {"EDGE_ID": 1, "NODEID_FROM": 1, "NODEID_TO": 1})
    assert net.graph["keys"][1] == (1, 1)
    assert len(net.edges()) == 1

    f = tempfile.NamedTemporaryFile(delete=False)
    fn = f.name

    loader.save_network_to_file(net, fn)

    net2 = loader.load_network_from_file(fn)
    assert net2.graph["keys"][1] == (1, 1)
    assert len(net2.edges()) == 1


def test_doctest():
    import doctest

    print(doctest.testmod(loader))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_doctest()
    test_add_edge()
    test_add_edge_missing_key()
    test_add_edge_with_reverse_lookup()
    test_create_graph()
    test_create_multidigraph()
    test_create_graph_no_lookup()
    test_load_network_from_records()
    test_load_network_from_records_missing_key()
    test_load_network_from_geometries()
    test_load_network_from_geometries_calculated_length()
    test_load_network_from_invalid_geometries()
    test_load_network_from_invalid_geometries_skip()
    test_load_network_from_invalid_geometries_missing_key()
    test_uniquedict()
    test_uniquedict_error()
    test_pickling()
    print("Done!")
