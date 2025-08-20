from wayfarer import loader, routing
from shapely.geometry import mapping
from shapely.ops import transform
import json
import pyproj

net = loader.load_network_from_file("./data/riga.pickle")
path = routing.solve_shortest_path(net, start_node=1390592196, end_node=1812435081)

features = []

transformer = pyproj.Transformer.from_crs(
    "EPSG:3857", "EPSG:4326", always_xy=True
).transform

for edge in path:
    # convert to EPSG:4326
    geom = transform(transformer, edge.attributes["geometry"])
    feature = {
        "type": "Feature",
        # convert the Shapely geometry to a GeoJSON geometry
        "geometry": mapping(geom),
        "properties": {"id": edge.key},
    }
    features.append(feature)

geojson_obj = {"type": "FeatureCollection", "features": features}

# save to a geojson file
with open("./data/riga.geojson", "w") as f:
    json.dump(geojson_obj, f, indent=4)

print("Done!")
