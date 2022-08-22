"""
A script to convert MultiLineStrings to LineStrings
"""

from shapely.geometry import shape
from shapely.geometry import mapping

def load_network_with_conversion(fgdb_path, layer_name):

    linestring_recs = []

    with fiona.open(fgdb_path, driver='FileGDB', layer=layer_name) as recs:

        # memory error in loop..
        for r in recs:
            geom = r['geometry']
            if geom['type'] == 'MultiLineString':
                # convert to shapely geometry
                shapely_geom = shape(geom)
                if(len(shapely_geom.geoms) == 1):
                    r['geometry'] = mapping(shapely_geom.geoms[0])
                    linestring_recs.append(r)


    net = loader.load_network(linestring_recs, key_field="LINK_ID", skip_errors=True)

layer_name = 'Accessibility_2015Net'
fgdb_path = r'C:\Data\NTA_Network_Datasets\Nta_Network.gdb'

load_network_with_conversion(fgdb_path, layer_name)