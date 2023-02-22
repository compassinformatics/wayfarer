"""
Helper module to convert between wayfarer and osmnx networks
"""
import wayfarer
from osmnx import utils  # , settings
import networkx as nx
from shapely import wkb
import osmnx as ox

from wayfarer import (
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
)


def to_osmnx(net, geometry_field: str = "Geometry4326", crs: str = "epsg:4326"):
    """
    Convert a wayfarer network into a osmnx network
    """
    metadata = {
        "created_date": utils.ts(),
        "created_with": f"OSMnx {ox.__version__}",
        "crs": crs,  # settings.default_crs, # epsg:4326
    }
    G = nx.MultiDiGraph(**metadata)  # wayfarer typically uses MultiGraph

    for tpl in net.edges(data=True, keys=True):

        edge = wayfarer.to_edge(tpl)

        edge_geometry = wkb.loads(edge.attributes[geometry_field])
        G.add_node(
            edge.start_node, x=edge_geometry.coords[0][0], y=edge_geometry.coords[0][1]
        )
        G.add_node(
            edge.end_node, x=edge_geometry.coords[-1][0], y=edge_geometry.coords[-1][1]
        )

        properties = {
            "osmid": edge.key,
            "name": "test",
            "highway": "highway",
            "oneway": False,
            "reversed": False,
            "length": edge.attributes[LENGTH_FIELD],
            "geometry": edge_geometry,
        }

        # merge with wayfarer fields
        edge.attributes.update(properties)
        G.add_edge(edge.start_node, edge.end_node, key=edge.key, **edge.attributes)

        # now add the reversed edge
        reversed_properties = edge.attributes.copy()
        reversed_properties.update(
            {
                "reversed": True,
                NODEID_FROM_FIELD: edge.end_node,
                NODEID_TO_FIELD: edge.start_node,
            }
        )
        # reversed_properties["reversed"] = True
        # reversed_properties["NODE_ID_FROM"] = edge.end_node
        # reversed_properties["NODE_ID_FROM"] = edge.start_node
        key = edge.key * -1

        G.add_edge(edge.end_node, edge.start_node, key=key, **reversed_properties)

    return G
