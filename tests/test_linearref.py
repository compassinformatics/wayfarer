import pytest
from wayfarer import linearref
from shapely.geometry import LineString, Point, MultiLineString
from decimal import Decimal


def test_invalid_lr():
    ls = LineString([(0, 0), (0, 100)])

    with pytest.raises(ValueError):
        linearref.create_line(ls, -1, 100)


def test_invalid_lr2():
    """
    Cannot have a LR feature with identical TO and FROM values
    """
    ls = LineString([(0, 0), (0, 100)])

    with pytest.raises(linearref.IdenticalMeasuresError):
        linearref.create_line(ls, 50, 50)


def test_invalid_lr3():
    """
    Cannot have a LR feature with a TO value greater than the line length
    """
    ls = LineString([(0, 0), (0, 100)])

    with pytest.raises(ValueError):
        linearref.create_line(ls, 0, 100.01)


def test_invalid_lr4():
    """
    Check if the length is outside the tolerance
    """
    ls = LineString([(0, 0), (0, 100)])

    tolerance = 1
    # acceptable
    linearref.create_line(ls, 0, 100.999, tolerance)

    tolerance = 1
    # not acceptable - outside tolerance

    with pytest.raises(ValueError):
        linearref.create_line(ls, 0, 101.001, tolerance)


def test_valid_lr():
    ls = LineString([(0, 0), (0, 100)])
    new_line = linearref.create_line(ls, 0, 50)
    assert type(new_line) is LineString
    assert new_line.is_valid
    assert new_line.length == 50
    expected = [(0.0, 0.0), (0.0, 50.0)]
    assert list(new_line.coords) == expected


def test_valid_lr2():
    ls = LineString([(0, 0), (0, 100)])
    new_line = linearref.create_line(ls, 1, 50)
    assert type(new_line) is LineString
    assert new_line.is_valid
    assert new_line.length == 49
    expected = [(0.0, 1.0), (0.0, 50.0)]
    assert list(new_line.coords) == expected


def test_ring_feature():
    """
    Test a ring feature
    """
    ls = LineString([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])

    assert ls.is_ring
    assert ls.length == 400

    new_line = linearref.create_line(ls, 0, 400)
    assert type(new_line) is LineString
    assert new_line.is_valid

    assert new_line.length == 400
    expected = [(0.0, 0.0), (0.0, 100.0), (100.0, 100.0), (100.0, 0.0), (0.0, 0.0)]

    assert list(new_line.coords) == expected
    assert new_line.length == 400


def test_find_common_vertex():
    ls1 = LineString([(0, 0), (0, 100)])
    ls2 = LineString([(0, 100), (0, 200)])

    pts = linearref.find_common_vertices(ls1, ls2)
    assert len(pts) == 1
    assert list(pts[0].coords) == [(0, 100)]


def test_find_common_vertex2():
    """
    Check that if two lines cross, but do not intersect NO common point is returned
    This is not a valid occurrence as the network should have been split.
    """

    ls1 = LineString([(0, 0), (0, 100)])
    ls2 = LineString([(50, -50), (50, 50)])

    pts = linearref.find_common_vertices(ls1, ls2)
    assert len(pts) == 0


def test_multiple_common_vertices():
    """
    Check that two lines that touch twice return all the touching
    vertices
    """

    ls1 = LineString([(0, 0), (0, 100), (100, 100), (100, 0)])
    ls2 = LineString([(0, 0), (100, 0)])

    pts = linearref.find_common_vertices(ls1, ls2)
    assert len(pts) == 2
    assert list(pts[0].coords) == [(0, 0)]
    assert list(pts[1].coords) == [(100, 0)]


def test_missing_common_vertex():
    """
    Check two line strings that don't join don't return a common point
    """
    ls1 = LineString([(0, 0), (0, 100)])
    ls2 = LineString([(0, 100.001), (0, 200)])

    pts = linearref.find_common_vertices(ls1, ls2)
    assert len(pts) == 0


def test_snap_to_ends():
    ls = LineString([(0, 0), (0, 100)])
    m_values = linearref.snap_to_ends(ls, 4, 96, tolerance=5)
    assert m_values == (0, 100)


def test_snap_to_ends2():
    ls = LineString([(0, 0), (0, 100)])
    m_values = linearref.snap_to_ends(ls, 4, 96, tolerance=3)
    assert m_values == (4, 96)


def test_snap_to_ends3():
    ls = LineString([(0, 0), (0, 100)])
    with pytest.raises(ValueError):
        linearref.snap_to_ends(ls, 96, 4, tolerance=5)


def test_is_partial():
    ls = LineString([(0, 0), (0, 100)])
    assert linearref.is_partial(ls, 0, 100) is False


def test_is_partial2():
    ls = LineString([(0, 0), (0, 100)])
    assert linearref.is_partial(ls, 0.1, 100)


def test_is_partial3():
    ls = LineString([(0, 0), (0, 100)])
    assert linearref.is_partial(ls, 0, 99.999)


def test_is_partial3b():
    ls = LineString([(0, 0), (0, 100)])
    assert linearref.is_partial(ls, 0, 99.999, tolerance=0.002) is False


def test_is_partial4():
    ls = LineString([(0, 0), (0, 100)])
    assert linearref.is_partial(ls, 0, 100) is False


def test_get_m_values():
    pt1 = Point(5, 0)
    pt2 = Point(95, 0)
    ls = LineString([(0, 0), (100, 0)])
    ms = linearref.get_measures(ls, pt1, pt2)
    assert ms == (5, 95)


def test_get_m_values2():
    pt1 = Point(4, 0)
    pt2 = Point(96, 0)

    ls = LineString([(0, 0), (100, 0)])
    ms = linearref.get_measures(ls, pt1, pt2)

    assert ms == (4, 96)


def test_get_m_values3():
    """
    Point order should not matter
    """
    pt1 = Point(96, 0)
    pt2 = Point(4, 0)

    ls = LineString([(0, 0), (100, 0)])
    ms = linearref.get_measures(ls, pt1, pt2)
    assert ms == (4, 96)


def test_get_end_point():
    ls = LineString([(0, 0), (100, 0)])
    input_point = Point(40, 0)
    common_vertices = [Point(0, 0), Point(100, 0)]

    res = linearref.get_end_point(ls, input_point, common_vertices)
    assert list(res.coords) == [(0.0, 0.0)]

    res = linearref.get_end_point(ls, Point(80, 0), common_vertices)
    assert list(res.coords) == [(100.0, 0.0)]

    # this is a point equi-distant between the two end points, it snaps to the start
    res = linearref.get_end_point(ls, Point(50, 0), common_vertices)
    assert list(res.coords) == [(0.0, 0.0)]

    # shifting it slightly will snap to the end
    res = linearref.get_end_point(ls, Point(50.1, 0), common_vertices)
    assert list(res.coords) == [(100.0, 0.0)]


def test_get_end_point2():
    ls = LineString([(30, 0), (30, 100), (70, 100), (70, 0)])
    input_point = Point(70, 100)
    common_vertices = [Point(30, 0), Point(70, 0)]

    res = linearref.get_end_point(ls, input_point, common_vertices)
    assert list(res.coords) == [(70.0, 0.0)]

    res = linearref.get_end_point(ls, Point(30, 50), common_vertices)
    assert list(res.coords) == [(30.0, 0.0)]


def test_get_end_point_error():

    ls = LineString([(30, 0), (30, 100), (70, 100), (70, 0)])
    input_point = Point(70, 100)
    # too many common vertices for 2 connecting lines
    common_vertices = [Point(30, 0), Point(70, 0), Point(70, 0)]

    with pytest.raises(ValueError):
        linearref.get_end_point(ls, input_point, common_vertices)


def test_ring():
    line = LineString(
        [
            (168764.57100460742, 68272.608483201067),
            (168832.93332556245, 68298.551410977932),
            (168883.42972378185, 68309.132574679476),
            (168886.35790014532, 68299.801526872063),
            (168887.16619741436, 68287.32007539396),
            (168853.44703749285, 68263.61740366694),
            (168852.87793392732, 68200.530325998014),
            (168789.0274291017, 68193.019515298161),
            (168780.06970638721, 68220.672574178898),
            (168764.57100460742, 68272.608483201067),
        ]
    )

    assert line.is_ring

    m_values = [183.07291799999999, 366.56121400000001]
    new_line = linearref.create_line(line, m_values[0], m_values[1])

    pytest.approx(new_line.length, m_values[1] - m_values[0], 3)
    # AssertionError: 161.59143850732218 != 183.48829600000002


def test_with_decimals():
    line = LineString(
        [
            (84689.6348601028, 29919.330092903132),
            (84687.432594077953, 29909.819003758097),
            (84686.236535025368, 29902.688215733091),
            (84686.310773797828, 29887.686476198891),
            (84686.863399977301, 29874.065014830347),
            (84686.253012411442, 29863.203702854349),
            (84685.593192687331, 29849.902211625373),
            (84688.290414040355, 29829.089909696544),
            (84691.276261255116, 29810.737785154419),
            (84693.60228874578, 29793.925923847732),
            (84697.86667247866, 29779.714284997921),
            (84701.702191497869, 29768.413072214124),
            (84705.669710675953, 29756.381695013002),
            (84701.355804249732, 29746.720619865046),
            (84691.43297749311, 29738.199729009848),
            (84689.469905171762, 29734.669302664308),
            (84689.181188774921, 29721.997810781715),
            (84691.993932900717, 29712.616825774101),
            (84695.48288360161, 29704.745874264907),
            (84701.034133080713, 29695.134794451256),
            (84705.620187982611, 29687.93401295822),
            (84706.791440420973, 29672.222223408633),
            (84710.239197656672, 29637.008300359623),
            (84711.691018333935, 29633.047797870815),
            (84711.163108233581, 29624.45691354759),
            (84710.494868746246, 29620.186381851963),
            (84709.134035832816, 29604.794620576053),
            (84703.376637957466, 29584.472389191658),
            (84700.250461355696, 29581.371980855274),
            (84695.433541978447, 29576.06137180372),
            (84686.72316112541, 29568.280528164498),
            (84680.190511288252, 29560.409576655304),
            (84677.361289776381, 29552.428693544738),
            (84672.197892615892, 29545.777976997306),
            (84663.075214970377, 29535.136818894589),
            (84659.14074109956, 29528.186014073093),
            (84653.424627224507, 29518.044925581675),
            (84647.947707052954, 29511.384093699158),
            (84645.002962768311, 29505.323380230664),
            (84645.044337303698, 29496.232426296145),
            (84647.114603169684, 29484.53107643556),
            (84649.201527491925, 29478.070400292607),
            (84652.038897161765, 29470.579471458255),
            (84651.676032527539, 29461.918593667),
            (84652.129613320314, 29453.117612671464),
            (84651.453316210114, 29442.246301628606),
            (84650.727405871483, 29433.535428503041),
            (84647.023887011121, 29426.254480072785),
            (84642.965742209577, 29416.803501597136),
            (84636.960911937684, 29408.252497273137),
            (84626.452504229426, 29391.790719574827),
            (84615.878096441724, 29375.728904550975),
            (84606.780225410417, 29355.696587971455),
            (84597.2368312092, 29328.253509494807),
            (84593.690119121908, 29305.200893382011),
            (84583.635292206425, 29268.926778575129),
            (84575.271479671705, 29256.045422556668),
            (84560.432688151137, 29238.73337537047),
            (84541.47799044264, 29229.972390642379),
            (84532.693461352217, 29226.582125635225),
            (84527.241438329962, 29223.771690237823),
            (84510.142528863085, 29215.370788184966),
            (84488.333893563569, 29207.579887344771),
            (84474.023012143356, 29203.519510455568),
            (84466.401496798251, 29201.549171076862),
            (84459.307891553501, 29199.848980905746),
            (84444.271190329731, 29200.989223332617),
            (84429.853115364866, 29203.499512321843),
            (84403.69761886698, 29206.929773596443),
            (84385.872889596547, 29208.439981497191),
            (84383.019042540633, 29211.690375836501),
            (84377.476122289649, 29219.011204265986),
            (84359.271960463826, 29228.612285012772),
            (84342.181380225069, 29235.843121840502),
            (84329.066467322336, 29239.963609399092),
            (84320.859371025595, 29240.963690487573),
        ]
    )

    m_values = [Decimal("0.000000"), Decimal("996.524166")]
    new_line = linearref.create_line(line, m_values[0], m_values[1])

    pytest.approx(new_line.length, float(m_values[1]) - float(m_values[0]), 3)


def test_get_measure_on_line():
    pt = Point(50, 0)
    ls = LineString([(0, 0), (100, 0)])

    m = linearref.get_measure_on_line(ls, pt)
    assert m == 50


def test_get_measure_not_on_line():
    pt = Point(500, 0)
    ls = LineString([(0, 0), (100, 0)])

    m = linearref.get_measure_on_line(ls, pt)
    assert m == 100  # the measure is set to the end of the line


def test_duplicate_coords():
    """
    Originally the following will failed, as if two points have the same coordinates
    (as magnitude is 0) a ZeroDivisionError: float division error is thrown
    This is resolved by removing duplicate points in the function
    """
    p = Point(1.5, 1.5)
    line = LineString([(0, 0), (1, 1), (1, 1), (2, 2)])
    ip, dist = linearref.get_nearest_vertex(p, line)

    assert dist == 0


def test_remove_duplicates_in_line():
    polyline = LineString([(0, 0), (1, 1), (1, 1), (2, 2)])
    polyline = linearref.remove_duplicates_in_line(polyline)
    assert list(polyline.coords) == [(0, 0), (1, 1), (2, 2)]


def test_remove_duplicates_in_multipolyline():
    polyline = MultiLineString(
        [[(0, 0), (1, 1), (1, 1), (2, 2)], [(0, 0), (1, 1), (1, 1), (2, 2)]]
    )

    with pytest.raises(NotImplementedError):
        polyline = linearref.remove_duplicates_in_line(polyline)


def test_get_closest_point_to_measure():
    ls = LineString([(0, 0), (0, 50), (0, 100)])
    points = [Point(0, 10), Point(0, 55)]
    res = linearref.get_closest_point_to_measure(ls, points, measure=20)
    assert res.x == 0
    assert res.y == 10


def test_intersect_point_to_line():

    point = Point(1, 50)
    start_point = Point(0, 0)
    end_point = Point(0, 100)
    pt = linearref.intersect_point_to_line(point, start_point, end_point)
    assert pt.x == 0
    assert pt.y == 50


def test_get_nearest_vertex():

    point = Point(2, 21)
    line = LineString([(0, 0), (0, 50), (0, 100)])
    pt, distance = linearref.get_nearest_vertex(point, line)
    print(pt, distance)
    assert pt.x == 0
    assert pt.y == 21
    assert distance == 2.0


def run_tests():
    pytest.main(["tests/test_linearref.py"])


if __name__ == "__main__":
    # run_tests()
    test_intersect_point_to_line()
    # test_get_end_point_error()
    print("Done!")
