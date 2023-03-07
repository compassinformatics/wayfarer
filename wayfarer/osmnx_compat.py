"""
Helper module to convert between wayfarer and osmnx networks
"""
import wayfarer
import networkx as nx
from shapely import wkb, LineString
import osmnx as ox
import logging
import datetime as dt


from wayfarer import (
    LENGTH_FIELD,
    NODEID_FROM_FIELD,
    NODEID_TO_FIELD,
)


log = logging.getLogger("wayfarer")


def to_osmnx(
    net: (nx.MultiGraph | nx.MultiDiGraph),
    geometry_field: str = "Geometry4326",
    crs: str = "epsg:4326",
) -> nx.MultiDiGraph:
    """
    Convert a wayfarer network into a osmnx network
    default_crs in osmnx is in settings.default_crs and is epsg:4326
    """

    # for timestamp see code from https://github.com/gboeing/osmnx/blob/3822ed659f1cc9f426a990c02dd8ca6b3f4d56d7/osmnx/utils.py#L50
    template = "{:%Y-%m-%d %H:%M:%S}"
    ts = template.format(dt.datetime.now())

    metadata = {
        "created_date": ts,
        "created_with": f"OSMnx {ox.__version__}",
        "crs": crs,
    }

    G = nx.MultiDiGraph(**metadata)  # wayfarer typically uses MultiGraph networks

    for tpl in net.edges(data=True, keys=True):

        edge = wayfarer.to_edge(tpl)

        try:
            edge_geometry = edge.attributes[geometry_field]
        except KeyError:
            keys = list(edge.attributes.keys())
            log.error(
                f"The attribute '{geometry_field}' was not found in the edge attributes: {keys}"
            )
            raise

        if not type(edge_geometry) is LineString:
            edge_geometry = wkb.loads(edge_geometry)

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
        key = edge.key * -1

        G.add_edge(edge.end_node, edge.start_node, key=key, **reversed_properties)

    return G
