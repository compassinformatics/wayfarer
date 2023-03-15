r"""
A FastAPI router to handle solving
upstream and downstream paths on a river network
"""

from fastapi import APIRouter
import logging
import osmnx as ox
import networkx as nx
from shapely.geometry import LineString, Point, Polygon
from wayfarer import loader
from pydantic import BaseModel
from functools import lru_cache
import geojson
import geopandas as gpd


router = APIRouter()
log = logging.getLogger("web")


class Coordinate(BaseModel):
    x: float
    y: float


@lru_cache
def get_readonly_network(fn):
    """
    Can't cache this as any splits etc. modify the underlying dictionary
    """
    log.debug(f"Loading network from {fn}")
    return loader.load_network_from_file(fn)


def make_iso_polys(
    G, center_node, trip_times, edge_buff=25, node_buff=50, infill=False
):
    isochrone_polys = []
    for trip_time in sorted(trip_times, reverse=True):
        subgraph = nx.ego_graph(G, center_node, radius=trip_time, distance="time")

        node_points = [
            Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)
        ]
        nodes_gdf = gpd.GeoDataFrame({"id": list(subgraph.nodes)}, geometry=node_points)
        nodes_gdf = nodes_gdf.set_index("id")

        edge_lines = []

        for n_fr, n_to in subgraph.edges():
            f = nodes_gdf.loc[n_fr].geometry
            t = nodes_gdf.loc[n_to].geometry

            # so get the first key for the edges between the nodes
            edges = G.get_edge_data(n_fr, n_to)
            edge_lookup = edges[next(iter(edges))].get("geometry", LineString([f, t]))

            edge_lines.append(edge_lookup)

        n = nodes_gdf.buffer(node_buff).geometry
        e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
        all_gs = list(n) + list(e)
        new_iso = gpd.GeoSeries(all_gs).unary_union

        # try to fill in surrounded areas so shapes will appear solid and
        # blocks without white space inside them
        if infill:
            new_iso = Polygon(new_iso.exterior)
        isochrone_polys.append(new_iso)

    return isochrone_polys


@router.post("/isochrones")
async def isochrones(
    isochrone_center: Coordinate, network_filename="../data/stbrice.osmnx.pickle"
):

    x = isochrone_center.x
    y = isochrone_center.y

    net = get_readonly_network(network_filename)
    # net = osmnx_compat.to_osmnx(net, geometry_field="geometry", crs="epsg:3857")

    # gdf_nodes = ox.graph_to_gdfs(net, edges=False)
    center_node = ox.distance.nearest_nodes(net, x, y)

    trip_times = [5, 10, 15, 20, 25, 30, 60]  # in minutes
    travel_speed = 4.5  # walking speed in km/hour

    # add an edge attribute for time in minutes required to traverse each edge
    meters_per_minute = travel_speed * 1000 / 60  # km per hour to m per minute
    for _, _, _, data in net.edges(data=True, keys=True):
        data["time"] = data["length"] / meters_per_minute

    # get one color for each isochrone
    iso_colors = ox.plot.get_colors(
        n=len(trip_times), cmap="plasma", start=0, return_hex=True
    )

    # make the isochrone polygons
    isochrone_polys = make_iso_polys(
        net, center_node, trip_times, edge_buff=25, node_buff=0, infill=True
    )

    feats = []
    for poly, time, color in zip(isochrone_polys, trip_times, iso_colors):
        f = geojson.Feature(
            id=time,
            geometry=poly.__geo_interface__,
            properties={"color": color, "time": time},
        )
        feats.append(f)

    # convert to GeoJSON
    return geojson.FeatureCollection(features=feats)


def test_isochrones():
    import asyncio

    # test_solve_shortest_path_from_points()
    iso = Coordinate(x=263316.62633553497, y=6275803.216269696)

    gj = asyncio.run(isochrones(iso, network_filename="./data/stbrice.osmnx.pickle"))

    print(gj)


if __name__ == "__main__":
    test_isochrones()
    print("Done!")
