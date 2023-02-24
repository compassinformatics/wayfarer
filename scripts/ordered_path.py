"""
Script to get an ordered path between edges, providing an index and a direction
"""

from wayfarer import loader, routing, functions

fn = r"./data/tipperary.txt"
net = loader.load_network_from_file(fn)

edges = []
# get edge_ids per ProjectId per Group (see SQL above)
edge_ids = [1393622, 1414298, 1425617, 1457705, 1464289, 1548367, 1573235]

for edge_id in edge_ids:
    edge = functions.get_edge_by_key(net, edge_id, with_data=True)
    edges.append(edge)

ordered_edges = routing.find_ordered_path(edges)

for idx, oe in enumerate(ordered_edges):
    print(idx, oe.attributes["EDGE_ID"], oe.attributes["WITH_DIRECTION"])
