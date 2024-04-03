r"""
This script generates images of the network used in the unit tests

$env:PYTHONPATH = 'D:\GitHub\wayfarer\tests;' + $env:PYTHONPATH
python D:\GitHub\wayfarer\scripts\create_network_images.py

"""

import os
from tests import networks
import networkx as nx
import matplotlib
import logging
import matplotlib.pyplot as plt
import wayfarer


def save_network_image_to_file(net, fn):

    matplotlib.use("Agg")

    f = plt.figure()
    ax = f.add_subplot(111)

    pos = nx.spring_layout(net)
    # pos = nx.bipartite_layout(net, net.nodes())

    nx.draw_networkx(net, pos=pos, ax=ax, with_labels=True)

    edge_labels = wayfarer.to_edges(
        net.edges(data=True, keys=True)
    )  # nx.get_edge_attributes(net,'EDGE_ID') # key is edge, pls check for your case
    edge_labels_dict = {(e.start_node, e.end_node): e.key for e in edge_labels}

    nx.draw_networkx_edge_labels(
        net, pos, edge_labels=edge_labels_dict, font_color="black"
    )

    logging.info(f"Saving {fn}...")
    plt.box(False)  # removes border box
    plt.savefig(fn)


def create_network_images(out_folder):

    network_functions = {
        "simple_network": networks.simple_network,
        "single_edge_loop_network": networks.single_edge_loop_network,
        "reverse_network": networks.reverse_network,
        "t_network": networks.t_network,
        "dual_path_network": networks.dual_path_network,
        "p_network": networks.p_network,
        "double_loop_network": networks.double_loop_network,
        "circle_network": networks.circle_network,
        "loop_middle_network": networks.loop_middle_network,
        "triple_loop_network": networks.triple_loop_network,
        "reversed_loop_network": networks.reversed_loop_network,
        "bottle_network": networks.bottle_network,
    }

    for name, func in network_functions.items():
        fn = os.path.join(out_folder, name + ".png")
        net = func()
        logging.debug((net.edges(data=True, keys=True)))
        save_network_image_to_file(net, fn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fld = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    out_folder = os.path.join(fld, "docs", "images")
    create_network_images(out_folder)
    print("Done!")
