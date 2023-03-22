import geojson
import math
from wayfarer import Edge, GEOMETRY_FIELD
import logging

log = logging.getLogger("wayfarer")

try:
    import fiona
    from fiona.model import Geometry
except ImportError:
    log.info("fiona is not available")

try:
    from shapely.geometry import shape
    from shapely.geometry import mapping
except ImportError:
    log.info("shapely is not available")


def edge_to_feature(edge: Edge):
    """
    Convert a wayfarer Edge to a GeoJSON feature
    """

    try:
        line = edge.attributes[GEOMETRY_FIELD]
    except KeyError:
        log.error(f"Edge: {edge}")
        log.error("Available properties: {}".format(",".join(edge.attributes.keys())))
        raise

    edge.attributes.pop(GEOMETRY_FIELD)

    # remove any Nan values that can't be converted to JSON
    for k, v in edge.attributes.items():
        if type(v) is float and math.isnan(v):
            edge.attributes[k] = None

    return geojson.Feature(
        id=edge.key, geometry=line.__geo_interface__, properties=edge.attributes
    )


def edges_to_featurecollection(edges: list[Edge]):
    """
    Convert a list of wayfarer Edges to a GeoJSON feature collection
    """

    features = [edge_to_feature(e) for e in edges]
    return geojson.FeatureCollection(features=features)


def convert_to_geojson(
    input_file: str,
    output_file: str,
    layer_name: str,
    driver_name: str = "GPKG",
    convert_multilinestring: bool = True,
) -> None:
    """
    Converts an input dataset to GeoJSON.
    Requires fiona and shapely
    Ensures each output feature has a unique id field, and that any MultiLineString features which consist
    of a single linestring are converted to linestrings.
    """

    with fiona.open(
        input_file, "r", driver=driver_name, layer=layer_name
    ) as datasource:
        geojson_schema = datasource.schema.copy()

        # set the geometry schema or we will get the following errors
        # Record's geometry type does not match collection schema's geometry type: 'LineString' != '3D MultiLineString'

        if convert_multilinestring:
            geojson_schema["geometry"] = "LineString"

        with fiona.open(
            output_file,
            "w",
            driver="GeoJSON",
            schema=geojson_schema,
            crs=datasource.crs,
            ID_GENERATE="YES",
        ) as geojson_datasource:
            # Loop through each feature in the datasource and write it to the GeoJSON file
            for feature in datasource:
                if convert_multilinestring:
                    geom = feature["geometry"]
                    if geom.type == "MultiLineString":
                        # convert to shapely geometry
                        shapely_geom = shape(geom)
                        if len(shapely_geom.geoms) == 1:
                            feature["geometry"] = Geometry.from_dict(
                                **mapping(shapely_geom.geoms[0])
                            )

                geojson_datasource.write(feature)
