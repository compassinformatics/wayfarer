from wayfarer import loader, routing, splitter
from shapely.geometry import mapping
from shapely.ops import transform
import json
import pyproj


net = loader.load_network_from_file("./data/riga.pickle")

# now split the network with the user entered points

start_split_edges = splitter.split_network_edge(net, 281, [55.395])
start_node = start_split_edges[0].start_node

end_split_edges = splitter.split_network_edge(net, 1103, [7.735])
end_node = end_split_edges[1].start_node

path = routing.solve_shortest_path(net, start_node=start_node, end_node=end_node)

features = []

transformer = pyproj.Transformer.from_crs(
    "EPSG:3857", "EPSG:4326", always_xy=True
).transform

for edge in path:
    # convert to EPSG:4326
    geom = transform(transformer, edge.attributes["geometry"])
    feature = {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": {"id": edge.key},
    }
    features.append(feature)

geojson_obj = {"type": "FeatureCollection", "features": features}

# save to a geojson file
with open("./data/riga2.geojson", "w") as f:
    json.dump(geojson_obj, f, indent=4)

print("Done!")
