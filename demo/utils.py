import json
from shapely.geometry import shape, Point
from collections import defaultdict
from wayfarer import (
    EDGE_ID_FIELD,
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
    GEOMETRY_FIELD,
)
from wayfarer import functions, splitter
from wayfarer.splitter import SPLIT_KEY_SEPARATOR


def get_geometry_for_edge(net, network_edge):
    return shape(
        network_edge.attributes[GEOMETRY_FIELD]
    )  # needs to be in the same projection


def add_edits_to_network(net, jsn: str):
    split_edge_keys = defaultdict(list)

    geojson_obj = json.loads(jsn)
    for idx, feature in enumerate(geojson_obj["features"]):
        feat_id = feature["id"]
        shapely_feature = shape(feature["geometry"])

        start_edge_id = feature["properties"]["startFeatureId"]
        start_network_edge = functions.get_edge_by_key(net, start_edge_id)
        start_line = get_geometry_for_edge(net, start_network_edge)

        end_edge_id = feature["properties"]["endFeatureId"]
        end_network_edge = functions.get_edge_by_key(net, end_edge_id)
        end_line = get_geometry_for_edge(net, end_network_edge)

        sp = Point(shapely_feature.coords[0])
        start_measure = splitter.get_measure_for_point(start_line, sp)
        start_node_id = splitter.get_split_node_for_measure(
            start_network_edge, start_line.length, start_measure
        )

        if SPLIT_KEY_SEPARATOR in str(start_node_id):
            # a split should take place
            split_edge_keys[start_edge_id].append((idx, start_node_id, start_measure))

        ep = Point(shapely_feature.coords[-1])
        end_measure = splitter.get_measure_for_point(end_line, ep)
        end_node_id = splitter.get_split_node_for_measure(
            end_network_edge, end_line.length, end_measure
        )

        if SPLIT_KEY_SEPARATOR in str(end_node_id):
            # a split should take place
            split_edge_keys[end_edge_id].append((idx, end_node_id, end_measure))

        # now add the newly drawn line as a geometry
        attributes = {
            EDGE_ID_FIELD: feat_id,
            LENGTH_FIELD: shapely_feature.length,
            NODEID_FROM_FIELD: start_node_id,
            NODEID_TO_FIELD: end_node_id,
            GEOMETRY_FIELD: shapely_feature,
        }

        functions.add_edge(
            net,
            key=feat_id,
            start_node=start_node_id,
            end_node=end_node_id,
            attributes=attributes,
        )

    return split_edge_keys
