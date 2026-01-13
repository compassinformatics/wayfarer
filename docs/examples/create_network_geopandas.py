"""
python ./docs/examples/create_network_geopandas.py
"""

import geopandas as gpd
from wayfarer import loader
import os


def load_network(input_lines, output_network, overwrite=False):

    lines = gpd.read_file(input_lines, layer="edges")
    # add a unique field
    lines["oid"] = range(1, len(lines) + 1)
    lines.drop(columns="key", inplace=True)
    print(lines.head())

    if not os.path.exists(output_network) or overwrite is True:
        net = loader.load_network_from_records(
            lines.to_dict("records"),
            key_field="oid",
            length_field="length",
            from_field="from",
            to_field="to",
        )
        loader.save_network_to_file(net, output_network)
    return loader.load_network_from_file(output_network)


if __name__ == "__main__":
    # works with any GDAL supported dataset
    input_lines = "./data/dublin.gpkg"
    output_network = "./data/net.pickle"
    net = load_network(input_lines, output_network, overwrite=False)
    print("Done!")
