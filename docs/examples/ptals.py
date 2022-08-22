"""
C:\VirtualEnvs\wayfarer\Scripts\activate

pip install numpy
pip install GDAL --extra-index-url https://pypi.compass.ie
pip install fiona --extra-index-url https://pypi.compass.ie
pip install shapely --extra-index-url https://pypi.compass.ie
pip install git+https://github.com/compassinformatics/wayfarer@main

C:\VirtualEnvs\wayfarer\Scripts\activate
python C:\GitHub\wayfarer\docs\examples\ptals.py

Preprocessing to convert MultiLineStrings to LineStrings
"""
import os
import wayfarer
from wayfarer import loader, routing, functions, Edge, EDGE_ID_FIELD
import fiona
import networkx


def get_network(fgdb_path, output_file, layer_name, key_field="OBJECTID"):
    """
    Returns the network if already created, otherwise generates
    a new network file from the FileGeoDatabase
    """
    if os.path.exists(output_file) is True:
        net = loader.load_network_from_file(output_file)
    else:
        with fiona.open(fgdb_path, driver="FileGDB", layer=layer_name) as recs:
            # strip_properties reduces the size of the network from over 1GB to 67MB
            net = loader.load_network(recs, key_field, strip_properties=True)

        print(
            "Saving new network file {} containing {} edges".format(
                output_file, len(net.edges())
            )
        )
        loader.save_network_to_file(net, output_file)

    return net


def analyse_network(net):
    """
    Check network for connectivity and subgraphs
    """
    print(
        "Network is connected? {}".format(
            networkx.algorithms.components.is_connected(net)
        )
    )

    sub_graphs = networkx.connected_components(net)
    print(networkx.number_connected_components(net))

    for i, nodes in enumerate(sub_graphs):
        print("subgraph {} has {} nodes".format(i, len(nodes)))

        if len(nodes) < 1000:
            edges = net.edges(nodes, data=True)
            edges = wayfarer.to_edges(edges)
            edge_ids = [edge.key for edge in edges]
            print(edge_ids)


def routing_example(net):
    """
    Routes between 2 nodes on the network
    """
    edge1 = functions.get_edge_by_key(net, 63684)
    edge2 = functions.get_edge_by_key(net, 238610)  # 417508

    path_edges = routing.solve_shortest_path(net, edge1.start_node, edge2.end_node)

    path_ids = [edge.key for edge in path_edges]
    print(path_ids)


if __name__ == "__main__":

    output_file = r"C:\Data\ptals.dat"
    fgdb_path = r"C:\Data\NTA_Network_Datasets\linestrings.fgb"
    layer_name = "linestrings"
    net = get_network(fgdb_path, output_file, layer_name)
    analyse_network(net)

    print("Done!")
