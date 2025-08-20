from shapely.geometry import shape, Point
from wayfarer import loader, to_edge, linearref


def get_closest_edge(net, pt):

    closest_line = None
    min_dist = float("inf")

    for edge in net.edges(data=True, keys=True):
        edge = to_edge(edge)
        geom = shape(edge.attributes["geometry"])
        dist = pt.distance(geom)
        if dist < min_dist:
            min_dist = dist
            closest_line = geom
            fid = edge.key

    # find snapped point on the line
    snap_point, _ = linearref.get_nearest_vertex(pt, closest_line)

    # get the measure along the line
    distance_along = linearref.get_measure_on_line(closest_line, snap_point)
    return (fid, distance_along)


net = loader.load_network_from_file("./data/riga.pickle")

start_pt = Point(2682555, 7748329)
end_pt = Point(2682585, 7747272)

print(get_closest_edge(net, start_pt))
# (281, 55.395036218377086)

print(get_closest_edge(net, end_pt))
# (1103, 7.734503415793048)
