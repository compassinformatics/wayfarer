.. sourcecode:: python

    # add in any loops (this includes self-loops)
    # see https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.cycles.find_cycle.html
    # values are returned as a list of directed edges in the form [(u, v, k), (u, v, k),..]
    # the algorithm returns the first cycle found, traversing from the start_node - however
    # we want to then ensure that only cycles containing the node are included

    #if start_node == end_node:
    #    try:
    #        loop_edges = cycles.find_cycle(net, start_node)
    #        loop_edges = (e for e in loop_edges if start_node in e)
    #        # now remove the key from the tuple
    #        nodes = ([e[:-1] for e in loop_edges])
    #        # now we can flatten into a list of nodes
    #        nodes = itertools.chain(*nodes)
    #        # now convert [(u, v), (u, v)] into a list of nodes without consecutive duplicates
    #        # e.g. (1,2),(2,1) becomes [1,2,1]
    #        nodes = [n[0] for n in itertools.groupby(nodes)]
    #        print("loop", nodes)
    #        all_shortest_paths.append(nodes) # = itertools.chain(all_shortest_paths, (nodes))
    #    except networkx.exception.NetworkXNoCycle:
    #        pass