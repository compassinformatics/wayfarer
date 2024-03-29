r"""
Load a large file and check performance
Uses pytest-benchmark
First requires the test dat files to be created by unzipping gis_osm_roads_free_1.zip
and running load_osm_network.py

cd D:/Github/Python/wayfarer
#./wayfarer-venv/Scripts/activate.ps1

pytest -v scripts/benchmarking.py

"""

import pytest
import copy
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


def test_cloning_network(benchmark):
    """
    971 ms seconds to clone - much slower than simply re-reading from disk
    """
    net = loader.load_network_from_file("./data/dublin.pickle")
    benchmark(clone_network, net)
