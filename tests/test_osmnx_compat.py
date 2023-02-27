from wayfarer import osmnx_compat
import wayfarer
from tests import networks
import logging
from shapely import wkb
from shapely.geometry import Point, LineString
import pytest


def test_to_osmnx_missing_geom():

    net = networks.simple_network()

    with pytest.raises(KeyError):
        osmnx_compat.to_osmnx(net)


def test_to_osmnx():

    net = networks.simple_network()

    assert len(net.edges()) == 4
    assert len(net.nodes()) == 5

    for e in wayfarer.to_edges(net.edges(keys=True, data=True)):
        e.attributes["Geometry4326"] = wkb.dumps(LineString([Point(0, 0), Point(0, 1)]))

    G = osmnx_compat.to_osmnx(net)

    assert len(G.edges()) == 8
    assert len(G.nodes()) == 5

    edges = list(wayfarer.to_edges(G.edges(keys=True, data=True)))

    keys = list(sorted(edges[0].attributes.keys()))

    # check all the edge keys for both wayfarer and osmnx are present
    assert keys == [
        "EDGE_ID",
        "Geometry4326",
        "LEN_",
        "NODEID_FROM",
        "NODEID_TO",
        "geometry",
        "highway",
        "length",
        "name",
        "oneway",
        "osmid",
        "reversed",
    ]


def test_doctest():
    import doctest

    print(doctest.testmod(osmnx_compat))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_to_osmnx()
    print("Done!")
