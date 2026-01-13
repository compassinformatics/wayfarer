Edge Solver
===========

The edge solver allows users to select edges to create segments. Segments can only have a maximum of two
unattached junctions to support linear referencing (measures / chainage).

Loops and circular segments are allowed. The use cases below detail the currently supported network types in wayfarer. 

..
    To note:

    + solver points are added wherever a user clicks - but the whole edge will be highlighted in yellow
    + points can be added to edges in any order and the routing will occur between all points - the path index
      will be preserved even in the cases where a user "back tracks" and clicks on previous edges
    + multiple points can be added to the same edge (however it will not affect the routing so has no purpose)

    .. image:: /images/edge_solver.png
        :align: center

Supported Segments
------------------

The following network types are supported by the edge solver.

.. image:: /images/simple_network.png
    :align: center
    :scale: 50%

As above but with nodes in different orders:

.. image:: /images/reverse_network.png
    :align: center
    :scale: 50%

A loop at either end of the segment:

.. image:: /images/p_network.png
    :align: center
    :scale: 50%

A segment with loops at both ends:

.. image:: /images/double_loop_network.png
    :align: center
    :scale: 50%

A circular segment composed of several edges:

.. image:: /images/circle_network.png
    :align: center
    :scale: 50%

A segment with an edge at one end that loops back onto itself:

.. image:: /images/single_edge_loop_network.png
    :align: center

A two segments with two further segments in the middle both connected to the same start and end nodes:

.. image:: /images/dual_path_middle_network.png
    :align: center
    :scale: 50%

Valid but Unsupported Segments
------------------------------

It should be possible to implement the following types if required. The current edge solver however does not support them. 

Loops in the middle of the segment are unsupported. 

.. image:: /images/loop_middle_network.png
    :align: center
    :scale: 50%

This also excludes loops in the middle with loops at the start and ends. 

.. image:: /images/triple_loop_network.png
    :align: center
    :scale: 50%

The case below is where a road joins back to itself (a single edge loop). 

.. image:: /images/dual_path_network_manual.png
    :align: center

..
    .. image:: /images/dual_path_network.png
        :align: center
        :scale: 50%


Invalid Segments
----------------

These segments have more than 2 ends. This means it is impossible to apply linear referencing to them, so they will never be
supported by the edge solver. 

.. image:: /images/t_network.png
    :align: center
    :scale: 50%