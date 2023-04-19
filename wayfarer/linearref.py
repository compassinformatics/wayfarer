r"""
This module contains functions relating to linear referencing.
Requires the Shapely module

Reference links:

+ https://pypi.org/project/ligeos/
+ https://www.gaia-gis.it/fossil/libspatialite/wiki?name=VirtualRouting
+ http://plugins.qgis.org/plugins/lrs/
+ http://blazek.github.io/lrs/release/help.1.2.0/index.html
+ `ogr2ogr_ZMs <https://gist.github.com/geographika/3ad5fe0c5459f1dae8d28a0ffc4b8459>`_

"""
import logging
import sys
from math import sqrt
import itertools
from itertools import islice as slice
from shapely.geometry import LineString, Point


log = logging.getLogger("wayfarer")


class IdenticalMeasuresError(Exception):
    """
    A custom exception to indicate the start and end measures are identical
    """

    pass


def check_valid_m(m_value: float, length: float, tolerance: float = 0.00001) -> bool:
    """
    Check that an m_value is a valid measure for the input length

    Args:
        m_value: The measure
        length: The length of the line
        tolerance: The tolerance the m-value can be beyond the length of the line
    Returns:
        If the line is valid

    >>> check_valid_m(m_value=10, length=20)
    True

    >>> check_valid_m(m_value=-0.213, length=20)
    Traceback (most recent call last):
    ...
    ValueError: The m value (-0.213) must be a positive number
    """

    if m_value < 0:
        raise ValueError(f"The m value ({m_value}) must be a positive number")

    if m_value > length + tolerance:
        raise ValueError(
            f"The m value ({m_value}) is higher than the line length ({length}), which is not supported"
        )

    return True


def create_line(
    line: LineString, start_m: float, end_m: float, tolerance: float = 0.00001
) -> LineString:
    """
    Create a new line feature based on a start and end measure
    This function also handles ring LineStrings (where start and end nodes are the same)

    Args:
        line: The original LineString
        start_m: The start measure to split the line
        end_m: The end measure to split the line
        tolerance: The tolerance the m-value can be beyond the length of the line
    Returns:
        A new line based on the original geometry between the two measures

    >>> ls = LineString([(0, 0), (0, 100)])
    >>> create_line(ls, start_m=0, end_m=50)
    <LINESTRING (0 0, 0 50)>
    """

    # convert any decimals to floats otherwise the comparison operators silently fail/are incorrect
    start_m, end_m = float(start_m), float(end_m)

    check_valid_m(start_m, line.length, tolerance)
    check_valid_m(end_m, line.length, tolerance)

    if start_m > end_m:
        raise ValueError(
            f"The start measure {start_m} must be less than the end measure {end_m}"
        )

    if start_m == end_m:
        raise IdenticalMeasuresError(
            f"The start measure {start_m} cannot be equal to the end measure {end_m}"
        )

    start_pt = None
    end_pt = None
    new_coords = []
    new_line = None

    for p in list(line.coords):
        # loop through all the coordinates of the original line
        distance_along = line.project(Point(p))

        if distance_along >= start_m:
            if start_pt is None:
                # create the start point
                start_pt = line.interpolate(start_m)
                new_coords.append(start_pt.coords[0])

            if distance_along < end_m:
                # add in the point just after the start point
                if distance_along != start_m:
                    # the point is not the start_pt
                    new_coords.append(p)
                else:
                    pass
                    # this is the same as the start point, unless the original feature
                    # is a ring, and needs to be closed
                    # if line.is_ring:
                    #    new_coords.append(p)

        if distance_along >= end_m:
            # create the end point, and then exit the loop
            end_pt = line.interpolate(end_m)
            new_coords.append(end_pt.coords[0])
            break

    # add an end point if the feature is a ring, and the to point
    # has not yet been added
    if line.is_ring and end_pt is None:
        end_pt = line.interpolate(end_m)
        new_coords.append(end_pt.coords[0])

    new_line = LineString(new_coords)

    return new_line


def find_common_vertices(line1: LineString, line2: LineString) -> list[Point]:
    """
    Find all the points common to both lines and return a list of touching points

    Args:
        line1: The first line
        line1: The second line
    Returns:
        A list of points shared between the lines

    >>> ls1 = LineString([(0, 0), (0, 100)])
    >>> ls2 = LineString([(0, 100), (0, 200)])
    >>> find_common_vertices(ls1, ls2)
    [<POINT (0 100)>]
    """
    touching_points = []

    # as one point will be common to both lines we only need to loop through
    # one feature's points
    points = [Point(p) for p in line2.coords]  # convert coords to Point feature

    for p in points:
        if p.intersects(line1):
            touching_points.append(p)

    return touching_points


def snap_to_ends(
    line: LineString, start_m: float, end_m: float, tolerance: float = 5
) -> tuple[float, float]:
    """
    If the measure values are within the set tolerance to the
    ends of a segment, then "snap" these values to the end.

    Args:
        line: The LineString
        start_m: The start measure
        end_m: The end measure
        tolerance: The tolerance the m-value can be beyond the length of the line
    Returns:
        A tuple of the new snapped measures

    >>> ls = LineString([(0, 0), (0, 100)])
    >>> snap_to_ends(ls, start_m=4, end_m=96, tolerance=5)
    (0, 100.0)
    >>> snap_to_ends(ls, start_m=4, end_m=96, tolerance=4)
    (4, 96)
    """

    check_valid_m(start_m, line.length, tolerance)
    check_valid_m(end_m, line.length, tolerance)

    if start_m > end_m:
        raise ValueError(
            f"The start measure {start_m} must be less than the end measure {end_m}"
        )

    # check if the measure is near the end of the line
    if (line.length - end_m) < tolerance:
        end_m = (
            line.length
        )  # line lengths can differ depending on the software so add a tolerance for any floating-point issues

    # check if the line is near the start of the line
    if (start_m) < tolerance:
        start_m = 0

    return start_m, end_m


def is_partial(
    line: LineString, start_m: float, end_m: float, tolerance: float = 0.00001
) -> bool:
    """
    Check if the measures cover a whole LineString or only a part of it

    Args:
        line: The LineString
        start_m: The start measure
        end_m: The end measure
        tolerance: The tolerance for the measures when comparing the start and end
    Returns:
        Boolean indicating if the measures only partially cover the line

    >>> ls = LineString([(0, 0), (0, 100)])
    >>> is_partial(ls, start_m=0.5, end_m=101, tolerance=1)
    False
    """

    check_valid_m(start_m, line.length, tolerance)
    check_valid_m(end_m, line.length, tolerance)

    if abs(tolerance - start_m) > tolerance:
        return True

    if abs(line.length - end_m) > tolerance:
        return True

    return False


def get_measures(line: LineString, pt1: Point, pt2: Point) -> tuple[float, float]:
    """
    Snap two points to a line and return the measures

    Args:
        line: The LineString
        pt1: A first point
        pt2: A second point
    Returns:
        A tuple of the start and end measures

    >>> ls = LineString([(0, 0), (100, 0)])
    >>> pt1 = Point(4, 0)
    >>> pt2 = Point(96, 0)
    >>> get_measures(ls, pt1, pt2)
    (4.0, 96.0)
    """

    m1 = line.project(pt1)
    m2 = line.project(pt2)
    start_m, end_m = sorted([m1, m2])

    return (start_m, end_m)


def get_measure_on_line(line: LineString, point: Point) -> float:
    """
    Return the measure along a line of a point

    Args:
        line: The LineString
        point: The point
    Returns:
        The measure (m-value) of the point along the line

    >>> line = LineString([(0, 0), (100, 0)])
    >>> point = Point(50, 0)
    >>> get_measure_on_line(line, point)
    50.0
    """
    return line.project(point)


def get_closest_point_to_measure(
    line: LineString, points: list[Point], measure: float
) -> Point:
    """
    Returns the point closest to the start measure from the
    list of points

    Args:
        line: The LineString
        points: A list of points to check
        measure: A measure along the line
    Returns:
        The measure (m-value) of the point along the line

    >>> ls = LineString([(0, 0), (0, 50), (0, 100)])
    >>> points = [Point(0, 10), Point(0, 55)]
    >>> get_closest_point_to_measure(ls, points, measure=20)
    <POINT (0 10)>
    >>> get_closest_point_to_measure(ls, points, measure=80)
    <POINT (0 55)>
    """
    measures_with_points = {}

    for point in points:
        m = line.project(point)
        measures_with_points[m] = point

    # find the closest point to the input measure
    key = min((abs(measure - i), i) for i in measures_with_points.keys())[1]

    closest_point = measures_with_points[key]
    return closest_point


def get_end_point(
    line: LineString, point: Point, common_vertices: list[Point]
) -> Point:
    """
    Get the start or end of the line closest to the input point

    Args:
        line: The input line
        point: The input point
        common_vertices: Points shared between the two lines
    Returns:
        The end point

    >>> ls = LineString([(0, 0), (100, 0)])
    >>> point = Point(30, 0)
    >>> common_vertices = [Point(0, 0), Point(70, 0)]
    >>> get_end_point(ls, point, common_vertices)
    <POINT (0 0)>
    """

    if len(common_vertices) == 2:
        start_m = line.project(point)
        end_point = get_closest_point_to_measure(line, common_vertices, start_m)
    elif len(common_vertices) == 1:
        # the line is a ring
        end_point = common_vertices[0]
    else:
        raise ValueError(
            f"Connected lines in the network should only touch 1 or 2 times (touches {len(common_vertices)} times)"
        )
    return end_point


def magnitude(pt1: Point, pt2: Point) -> float:
    """
    Return the magnitude (distance) between two points

    Args:
        pt1: The first point
        pt2: The second point
    Returns:
        The distance between the two points

    >>> pt1 = Point(0, 0)
    >>> pt2 = Point(100, 100)
    >>> round(magnitude(pt1, pt2))
    141
    """
    vect_x = pt2.x - pt1.x
    vect_y = pt2.y - pt1.y
    return sqrt(vect_x**2 + vect_y**2)


def remove_duplicates_in_line(line: LineString):
    """
    Remove any duplicate coordinates from a LineString
    Note this does not work with MultiLineStrings

    Args:
        line: The LineString
    Returns:
        A new LineString with any duplicate coordinates removed

    >>> ls = LineString([(0, 0), (1, 1), (1,1)])
    >>> remove_duplicates_in_line(ls)
    <LINESTRING (0 0, 1 1)>
    """

    if line.geom_type != "LineString":
        raise NotImplementedError(f"Geometry type {line.geom_type} is not valid")

    clean_coords = [k for k, g in itertools.groupby(line.coords)]
    return LineString(clean_coords)


def intersect_point_to_line(
    point: Point, start_point: Point, end_point: Point
) -> Point:
    """
    Get the closest point to the input point, on a straight line
    created between start point and the end point

    >>> point = Point(1, 60)
    >>> start_point = Point(0, 0)
    >>> end_point = Point(0, 100)
    >>> intersect_point_to_line(point, start_point, end_point)
    <POINT (0 60)>

    Args:
        point: The input point to place along a line
        start_point: The start point of a straight line
        end_point: The end point of a straight line
    Returns:
        A point along the straight line, or the closest end point if beyond the start and end
        points of the line

    The function will fail if two points have the same coordinates (as magnitude is 0)
    with ``ZeroDivisionError: float division``

    From the `Shapely Manual <https://shapely.readthedocs.io/en/stable/manual.html>`_ the definition of a LineString is
    "Repeated points in the ordered sequence are allowed, but may incur performance penalties and should be avoided.
    A LineString may cross itself (i.e. be complex and not simple)."
    """

    line_magnitude = magnitude(start_point, end_point)

    try:
        assert line_magnitude != 0
    except AssertionError:
        log.error("Magnitude is 0 between the two points")
        raise

    # calculate the position of a point on a line segment in 2D space
    u = (
        (point.x - start_point.x) * (end_point.x - start_point.x)
        + (point.y - start_point.y) * (end_point.y - start_point.y)
    ) / (line_magnitude**2)

    # if the closest point does not fall along the line
    # then return whichever of the end points is closest to the point

    if u < 0.00001 or u > 1:
        ix = magnitude(point, start_point)
        iy = magnitude(point, end_point)
        if ix > iy:
            return end_point
        else:
            return start_point
    else:
        ix = start_point.x + u * (end_point.x - start_point.x)
        iy = start_point.y + u * (end_point.y - start_point.y)
        return Point([ix, iy])


def get_nearest_vertex(point: Point, line: LineString) -> tuple[Point, float]:
    """
    Get the point on the line that is closest to the input point
    Based on code from `gis.stackexchange.com <http://gis.stackexchange.com/questions/396/nearest-neighbor-between-a-point-layer-and-a-line-layer>`_

    Args:
        point: The input point to place along a line
        line: The input line
    Returns:
        A tuple containing the snapped point along the line
        and its distance from the original point

    >>> point = Point(2, 21)
    >>> line = LineString([(0, 0), (0, 50), (0, 100)])
    >>> get_nearest_vertex(point, line)
    (<POINT (0 21)>, 2.0)
    """

    # remove duplicates or we will get errors with the magnitude function later on
    line = remove_duplicates_in_line(line)

    nearest_point = None
    min_dist = float(sys.maxsize)

    # loop through pairs of points
    # slice slices list but returns an iterator
    for seg_start, seg_end in zip(line.coords, slice(line.coords, 1, None)):
        line_start = Point(seg_start)
        line_end = Point(seg_end)

        intersection_point = intersect_point_to_line(point, line_start, line_end)
        cur_dist = magnitude(point, intersection_point)

        if cur_dist < min_dist:
            min_dist = cur_dist
            nearest_point = intersection_point

    log.debug(
        f"Closest point found at: {nearest_point}, with a distance of {min_dist:.2f} units."
    )

    return nearest_point, min_dist


def get_closest_line(lines: list[LineString], point: Point) -> tuple[int, Point]:
    """
    Get the closest line to a point
    """
    closest_features = []

    for code, line in lines:
        if line.geom_type != "MultiLineString":
            if line.coords[0] == line.coords[-1]:
                log.warning(
                    "Circular feature/roundabout. Removing last point to continue. "
                )
                # the magnitude of the line is messed up if try to get vertex on this
                # so try again removing last vertex
                line = LineString(line[:-1])

            closest_point, dist = get_nearest_vertex(point, line)
            closest_features.append((dist, code, closest_point))
        else:
            raise ValueError("MultiLineString comparisons not supported")

    # now we have a tuple of ids and distances, we can find the closest
    # http://stackoverflow.com/questions/644170/how-does-python-sort-a-list-of-tuples
    # if both features are equal distances, then the sorting order of the ID will take
    # precedent

    assert len(closest_features) > 0

    code = sorted(closest_features)[0][1]  # this accesses the Id
    snapped_point = sorted(closest_features)[0][2]  # this accesses the point

    return (code, snapped_point)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
    print("Done!")
