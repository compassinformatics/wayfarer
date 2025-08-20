import networkx
from wayfarer import Edge, to_edge
from wayfarer import functions

net = networkx.MultiGraph()
edge = Edge(start_node=0, end_node=1, key=1, attributes={})

# use the helper function to add the Edge named tuple to the network
functions.add_edge(net, *edge)

# use some networkx functions to get edges back
node_ids = [1]
edges = net.edges(nbunch=node_ids, data=True, keys=True)

# now use the to_edge function to convert back to a named tuple
edges = [to_edge(e) for e in edges]
edge = edges[0]

# now we can access the properties as below
print(edge.key)
print(edge.start_node)
print(edge.end_node)
print(edge.attributes)
