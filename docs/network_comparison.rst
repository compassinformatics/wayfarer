Comparing Networks
==================


Used in the Pavement Management System to transfer data from one road network to another
by comparing lines.

Pass in a distance so the path that is closest to this distance is returned
A key can also be included to ensure that a particular edge id is included.


wayfarer.routing.solve_matching_path(net, start_node_id, end_node_id, distance=original_length, 
                                                      cutoff=cutoff, include_key=edge_to_include)
