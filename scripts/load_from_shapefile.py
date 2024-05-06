"""
An example of create a Wayfarer network using 
the pyshp library

pip install pyshp
"""

from wayfarer import loader
import shapefile

shpfile = "./data/gis_osm_roads_free_1.shp"
sf = shapefile.Reader(shpfile)

records = []
# convert the shapefile records into the JSON-like __geo_interface__ records
for shaperec in sf.shapeRecords():
    records.append(shaperec.__geo_interface__)

# print a sample record
print(records[0])

# use the load_network_from_geometries function to create the network
# using __geo_interface__ records
net = loader.load_network_from_geometries(records, key_field="osm_id")

print(f"Network contains {len(net.edges())} edges")

print("Done!")