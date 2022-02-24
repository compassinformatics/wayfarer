from wayfarer import loader


def simple_features():
    """
    Create a list of features representing a network
    There are 3 features in a flat line running from 0,0 to 300,0
    Each feature is 100 units in length
    """
    return [
        {
            "properties": {"EDGE_ID": 1},
            "geometry": {"type": "LineString", "coordinates": [(0, 0), (100, 0)]},
        },
        {
            "properties": {"EDGE_ID": 2},
            "geometry": {"type": "LineString", "coordinates": [(100, 0), (200, 0)]},
        },
        {
            "properties": {"EDGE_ID": 3},
            "geometry": {"type": "LineString", "coordinates": [(200, 0), (300, 0)]},
        },
    ]


if __name__ == "__main__":
    feats = simple_features()
    net = loader.load_network(feats, use_reverse_lookup=True)
    print("Done!")
