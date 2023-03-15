"""
pip install uvicorn[standard]
pip install fastapi

"""

from fastapi import APIRouter
from pydantic import BaseModel
from wayfarer import routing, loader, io, functions, splitter
from wayfarer.splitter import SPLIT_KEY_SEPARATOR
import logging
import json
from shapely.geometry import shape
from collections import defaultdict
from . import utils

log = logging.getLogger("web")

router = APIRouter()


def get_network(fn):
    """
    Can't cache this as any splits etc. modify the underlying dictionary
    """
    log.debug(f"Loading network from {fn}")
    return loader.load_network_from_file(fn)


class ShortestPathPoints(BaseModel):
    points: str
    edits: str | None


@router.post("/solve_shortest_path_from_points")
async def solve_shortest_path_from_points(
    shortest_path_points: ShortestPathPoints, network_filename="../data/rivers.pickle"
):
    net = get_network(network_filename)
    points_geojson = json.loads(shortest_path_points.points)

    if shortest_path_points.edits:
        split_edge_keys = utils.add_edits_to_network(net, shortest_path_points.edits)
    else:
        split_edge_keys = defaultdict(list)

    nodes = []

    for feature in points_geojson["features"]:
        edge_id = feature["properties"]["edgeId"]
        index = feature["properties"]["index"]
        point = shape(feature["geometry"])

        network_edge = functions.get_edge_by_key(net, edge_id)
        line = utils.get_geometry_for_edge(net, network_edge)
        measure = splitter.get_measure_for_point(line, point)
        node_id = splitter.get_split_node_for_measure(
            network_edge, line.length, measure
        )
        if SPLIT_KEY_SEPARATOR in str(node_id):
            # a split should take place
            split_edge_keys[edge_id].append((index, node_id, measure))
        nodes.append((index, node_id))

    for edge_id, v in split_edge_keys.items():
        measures = [n[2] for n in v]
        splitter.split_network_edge(net, edge_id, measures)

    # make sure nodes are sorted by the order they are entered in the UI
    sorted_nodes = [n[1] for n in sorted(nodes)]  # type: list[int| str]
    route_nodes = routing.solve_shortest_path_from_nodes(net, sorted_nodes)

    edges = functions.get_edges_from_nodes(net, route_nodes, with_direction_flag=True)

    for e in edges:
        if e.attributes.get("IS_SPLIT", False):
            e.attributes["FROM_M"] = int(e.attributes["OFFSET"])
            e.attributes["TO_M"] = int(e.attributes["OFFSET"] + e.attributes["LEN_"])
        else:
            e.attributes["FROM_M"] = 0
            e.attributes["TO_M"] = int(e.attributes["LEN_"])

    # convert to GeoJSON
    return io.edges_to_featurecollection(edges)


def test_solve_shortest_path_from_points():
    import asyncio

    edits = (
        '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"LineString",'
        '"coordinates":[[262895.2264031371,6275790.488930107],[262901.97236427915,6275683.27458231]]},"properties":'
        '{"startFeatureId":460,"endFeatureId":462},"id":-1},{"type":"Feature","geometry":{"type":"LineString","coordinates":'
        '[[263326.24433953955,6275855.110074056],[263367.6774540128,6275880.598906959]]},"properties":{"startFeatureId":2281,"endFeatureId":691},"id":-2}]}'
    )
    points = (
        '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point",'
        '"coordinates":[263316.62633553497,6275803.216269696]},"properties":{"edgeId":513,"index":0}},{"type":"Feature",'
        '"geometry":{"type":"Point","coordinates":[263175.7078335048,6276212.917601578]},"properties":{"edgeId":692,"index":1}}]}'
    )

    sp = ShortestPathPoints(points=points, edits=edits)
    print(sp.points)
    edges = asyncio.run(
        solve_shortest_path_from_points(sp, network_filename="./data/stbrice.pickle")
    )
    print(edges)


if __name__ == "__main__":
    test_solve_shortest_path_from_points()
    print("Done!")
