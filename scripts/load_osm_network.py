"""
pip install numpy
pip install fiona --extra-index-url ...

Run from root of project
python scripts/load_osm_network.py
"""

import fiona
from wayfarer import loader, functions


def main(shp):
    """
    154 MB without reversed lookup
    164 MB with lookup
    """
    recs = fiona.open(shp, "r")
    net = loader.load_network_from_geometries(recs, key_field="osm_id")

    print(net.name)
    print(net.graph["keys"][618090637])

    output_file = "./data/osm_ireland.dat"
    loader.save_network_to_file(net, output_file)

    print(net.name)

    test_key = 618090637
    edge1 = net.graph["keys"][test_key]
    edge2 = functions.get_edge_by_key(net, test_key)

    print(edge1, edge2)
    assert edge1[0] == edge2.start_node
    assert edge1[1] == edge2.end_node

    net = loader.load_network_from_geometries(
        recs, key_field="osm_id", use_reverse_lookup=False
    )
    output_file = "./data/osm_ireland_no_lookup.dat"
    loader.save_network_to_file(net, output_file)
    net = loader.load_network_from_file(output_file)
    print(net.name)
    edge = functions.get_edge_by_key(net, test_key)
    print(edge)


if __name__ == "__main__":
    shp = "./data/gis_osm_roads_free_1.shp"
    main(shp)
    print("Done!")
