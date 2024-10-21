r"""
Load a large file and check performance
Uses pytest-benchmark
First requires the test dat files to be created by unzipping gis_osm_roads_free_1.zip
and running load_osm_network.py

C:\VirtualEnvs\wayfarer\Scripts\activate.ps1
cd D:/Github/wayfarer

pytest -v scripts/benchmarking.py

"""

import pytest
import copy
import marshal
import networkx
from wayfarer import loader, functions


@pytest.fixture
def get_network():
    net = loader.load_network_from_file("./data/osm_ireland.dat")
    return net


def xtest_get_edge_by_key(get_network):
    net = get_network
    edge = functions.get_edge_by_key(net, 618090637)
    print(edge)


def test_lookup_speed_with_reverse_lookup(benchmark):
    net = loader.load_network_from_file("./data/osm_ireland.dat")
    benchmark(functions.get_edge_by_key, net, 151364)


def test_lookup_speed_without_reverse_lookup(benchmark):
    net = loader.load_network_from_file("./data/osm_ireland_no_lookup.dat")
    benchmark(functions.get_edge_by_key, net, 151364)


def get_edge_by_key():
    net = loader.load_network_from_file("./data/osm_ireland.dat")
    edge = functions.get_edge_by_key(net, 618090637, with_data=False)
    print(edge)  # ((-9.4357979, 51.9035691), (-9.4359127, 51.9036818), 618090637)
    edge = functions.get_edge_by_key(net, 618090637, with_data=True)
    print(edge)  # ((-9.4357979, 51.9035691), (-9.4359127, 51.9036818), 618090637)

    # following works but is slow
    # edges = networkx.get_edge_attributes(net, "EDGE_ID")
    # mapping = {y:x for x,y in edges.items()}
    # edge = mapping[618090637]
    print(edge)  # ((-9.4357979, 51.9035691), (-9.4359127, 51.9036818), 618090637)


def test_loading_network(benchmark):
    """
    125 ms
    """
    benchmark(loader.load_network_from_file, "./data/dublin.pickle")


def clone_network(net):
    copy.deepcopy(net)


def marshal_network(net):
    marshal.loads(marshal.dumps(net))


def test_cloning_network(benchmark):
    """
    971 ms seconds to clone - much slower than simply re-reading from disk
    """
    net = loader.load_network_from_file("./data/dublin.pickle")
    benchmark(clone_network, net)


def xtest_marshal_network(benchmark):
    """
    ValueError: unmarshallable object - it is not possible to
    use marshal.dumps on the networkx network
    """
    net = loader.load_network_from_file("./data/dublin.pickle")
    benchmark(marshal_network, net)


def test_get_edges_from_nodes_all_lengths(benchmark):
    """
    pytest -v scripts/benchmarking.py -k "test_get_edges_from_nodes_all_lengths"

    with copy.deepcopy - min 7.4000
    with marshal - min 4.9000

    When running path solving with over 100,000 iterations:
    marshal: 588 seconds
    copy.deepcopy: 660 seconds

    See discussions at https://stackoverflow.com/a/55157627/179520
    """
    net = networkx.MultiGraph()

    net.add_edge(1, 2, key="A", **{"EDGE_ID": "A", "LEN_": 50})
    net.add_edge(1, 2, key="B", **{"EDGE_ID": "B", "LEN_": 100})

    node_list = [1, 2]
    benchmark(functions.get_edges_from_nodes, net, node_list, shortest_path_only=False)
