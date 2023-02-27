"""
wayfarer can only use LineStrings for its networks
This helper script converts MultiLineStrings to LineStrings
"""

from shapely.geometry import shape
from shapely.geometry import mapping
import fiona
from wayfarer import loader


def load_network_with_conversion(fgdb_path, layer_name, key_field="LINK_ID"):

    linestring_recs = []

    with fiona.open(fgdb_path, driver="FileGDB", layer=layer_name) as recs:

        # memory error in loop..
        for r in recs:
            geom = r["geometry"]
            if geom["type"] == "MultiLineString":
                # convert to shapely geometry
                shapely_geom = shape(geom)
                if len(shapely_geom.geoms) == 1:
                    r["geometry"] = mapping(shapely_geom.geoms[0])
                    linestring_recs.append(r)

    net = loader.load_network_from_geometries(
        linestring_recs, key_field=key_field, skip_errors=True
    )
    return net


if __name__ == "__main__":

    layer_name = "ExampleLayer"
    fgdb_path = r"./data/network.gdb"

    load_network_with_conversion(fgdb_path, layer_name)
