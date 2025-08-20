import osmnx as ox
from wayfarer import loader
from osmnx import convert, projection


def download_osm():
    """
    Download roads from OSM centered around Riga, Latvia
    This only needs to be run once.
    """

    location_point = (56.94105, 24.09682)
    # get roads within a distance of 500m from this point
    bbox = ox.utils_geo.bbox_from_point(location_point, dist=500)

    G = ox.graph_from_bbox(bbox=bbox)

    # save as a graph
    ox.save_graphml(G, filepath="./data/riga.graphml")

    # also save the data as a GeoPackage for review (not required for routing)
    ox.save_graph_geopackage(G, filepath="./data/riga.gpkg")


def create_wayfarer_graph():

    # load the OSMnx graph from the previously saved file
    G = ox.load_graphml("./data/riga.graphml")

    # get data frames from the graph
    _, gdf_edges = convert.graph_to_gdfs(convert.to_undirected(G))

    # project to Web Mercator from EPSG:4326 so we can work with planar distance calculations
    gdf_edges = projection.project_gdf(gdf_edges, to_crs="EPSG:3857")

    # get a dictionary of all edges in the network
    d = gdf_edges.to_dict("records")

    # loop through the edges and add a unique key
    recs = []

    for fid, props in enumerate(d):
        # we can't use osmid as the key as sometimes it is not always unique and sometimes a list
        # instead use the enumerator which will match the FID in the GeoPackage
        props.update({"key": fid})
        # we reprojected the geometry to Web Mercator, so we also need to update the length field
        props["length"] = props["geometry"].length
        recs.append(props)

    # create the wayfarer network
    net = loader.load_network_from_records(
        recs,
        key_field="key",
        length_field="length",
        from_field="from",
        to_field="to",
    )

    # save the network
    loader.save_network_to_file(net, "./data/riga.pickle")


if __name__ == "__main__":
    download_osm()
    create_wayfarer_graph()
    print("Done!")
