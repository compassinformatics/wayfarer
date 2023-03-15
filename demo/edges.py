"""
pip install uvicorn[standard]
pip install fastapi

"""

from fastapi import APIRouter
from pydantic import BaseModel
from wayfarer import routing, loader, io
import logging
from . import utils


log = logging.getLogger("web")

router = APIRouter()


class ShortestPath(BaseModel):
    path: list[int | str]
    edits: str | None


def get_network(fn):
    """
    Can't cache this as any splits etc. modify the underlying dictionary
    """
    log.debug(f"Loading network from {fn}")
    return loader.load_network_from_file(fn)


@router.post("/solve_shortest_path_from_edges")
async def solve_shortest_path_from_edges(
    shortest_path: ShortestPath, network_filename="../data/dublin.pickle"
):
    # net.copy() returns a shallow copy of the network, so attribute dicts are shared
    # need to use deepcopy here or the network is modified each time
    # net = deepcopy(get_network(network_filename))

    log.info("Starting solve")
    net = get_network(network_filename)
    # add in the network modifications

    if shortest_path.edits:
        utils.add_edits_to_network(net, shortest_path.edits)

    # now run the routing - but what happens when the edges in the path are now split?
    edges = routing.solve_shortest_path_from_edges(net, shortest_path.path)

    for idx, e in enumerate(edges):
        e.attributes["index"] = idx

    # convert to GeoJSON
    return io.edges_to_featurecollection(edges)


def test_solve_shortest_path_from_edges():

    import asyncio

    edits = (
        '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"LineString",'
        '"coordinates":[[-699847.2947505378,7047362.468482355],[-699908.6370419887,7047120.352018594]]},'
        '"properties":{"startFeatureId":2401,"endFeatureId":2403},"id":-1}]}'
    )

    edits = (
        '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"LineString",'
        '"coordinates":[[-699080.4219181875,7047263.789299513],[-698924.1756441435,7047311.084258694]]},'
        '"properties":{"startFeatureId":227,"endFeatureId":1254},"id":-1}]}'
    )

    sp = ShortestPath(path=[384, 1575], edits=edits)
    print(sp.path)
    edges = asyncio.run(
        solve_shortest_path_from_edges(sp, network_filename="./data/dublin.pickle")
    )
    print(edges)


if __name__ == "__main__":
    test_solve_shortest_path_from_edges()
    print("Done!")
