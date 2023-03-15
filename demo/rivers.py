r"""
A FastAPI router to handle solving
upstream and downstream paths on a river network
"""

from fastapi import APIRouter
from networkx.algorithms.dag import descendants
from networkx.algorithms.dag import ancestors
from wayfarer import (
    loader,
    functions,
    splitter,
    io,
    WITH_DIRECTION_FIELD,
    LENGTH_FIELD,
    GEOMETRY_FIELD,
)
import wayfarer
from wayfarer.splitter import SPLIT_KEY_SEPARATOR
from functools import lru_cache
import logging
from pydantic import BaseModel
from shapely.geometry import shape, Point

router = APIRouter()
log = logging.getLogger("web")


# @lru_cache
def get_network(fn):
    """
    Can't cache this as any splits etc. modify the underlying dictionary
    """
    log.debug(f"Loading network from {fn}")
    return loader.load_network_from_file(fn)


@lru_cache
def get_readonly_network(fn):
    """
    Can't cache this as any splits etc. modify the underlying dictionary
    """
    log.debug(f"Loading network from {fn}")
    return loader.load_network_from_file(fn)


class Coordinate(BaseModel):
    x: float
    y: float
    edge_id: int


def split_start_edge(net, edge_id, input_point):

    start_network_edge = functions.get_edge_by_key(net, edge_id)

    start_line = shape(
        start_network_edge.attributes[GEOMETRY_FIELD]
    )  # needs to be in the same projection

    start_measure = splitter.get_measure_for_point(start_line, input_point)
    start_node_id = splitter.get_split_node_for_measure(
        start_network_edge, start_line.length, start_measure
    )

    if SPLIT_KEY_SEPARATOR in start_node_id:
        splitter.split_network_edge(net, edge_id, [start_measure])

    return start_node_id


def get_upstream_edges(net, node_id):

    upstream_nodes_ids = ancestors(
        net, node_id
    )  # use node_id_from as we will add the start edge separately

    upstream_nodes_ids.add(
        node_id
    )  # make sure we include the start node as well as the ancestors

    return net.in_edges(nbunch=upstream_nodes_ids, data=True, keys=True)


def get_downstream_edges(net, node_id):
    """
    Note this returns the edges in a random order
    """
    downstream_nodes_ids = descendants(
        net, node_id
    )  # use node_id_to as we will add the start edge separately
    downstream_nodes_ids.add(
        node_id
    )  # make sure we include the start node as well as the ancestors
    return net.out_edges(nbunch=downstream_nodes_ids, data=True, keys=True)


@router.post("/solve_upstream")
async def solve_upstream(coords: Coordinate, network_filename="../data/rivers.pickle"):
    net = get_network(network_filename)

    edge_id = coords.edge_id
    start_point = Point(coords.x, coords.y)

    start_node_id = split_start_edge(net, edge_id, start_point)

    edges = get_upstream_edges(net, start_node_id)
    edges = wayfarer.to_edges(edges)

    for e in edges:
        e.attributes[WITH_DIRECTION_FIELD] = True
        e.attributes["FROM_M"] = 0
        e.attributes["TO_M"] = e.attributes[LENGTH_FIELD]

    # convert to GeoJSON
    return io.edges_to_featurecollection(edges)


@router.post("/solve_downstream")
async def solve_downstream(
    coords: Coordinate, network_filename="../data/rivers.pickle"
):
    net = get_network(network_filename)

    edge_id = coords.edge_id
    start_point = Point(coords.x, coords.y)

    start_node_id = split_start_edge(net, edge_id, start_point)

    edges = get_downstream_edges(net, start_node_id)
    edges = wayfarer.to_edges(edges)

    for e in edges:
        e.attributes[WITH_DIRECTION_FIELD] = True
        e.attributes["FROM_M"] = 0
        e.attributes["TO_M"] = e.attributes[LENGTH_FIELD]

    # convert to GeoJSON
    return io.edges_to_featurecollection(edges)


def test_solve_downstream():
    net = get_network("./data/rivers.pickle")
    print(functions.get_edge_by_key(net, 3))
    print(functions.get_edge_by_key(net, 2287))
    import asyncio

    coords = Coordinate(x=-1069103.5981220326, y=6866053.86210237, edge_id=129)
    gj = asyncio.run(solve_downstream(coords, network_filename="./data/rivers.pickle"))
    print(gj)


if __name__ == "__main__":
    test_solve_downstream()
    print("Done!")
