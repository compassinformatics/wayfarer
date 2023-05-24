Wayfarer
========

| |Coveralls|

A Python library for creating and analysing geospatial networks using `NetworkX <https://networkx.org/>`_.

For an overview presentation see https://compassinformatics.github.io/wayfarer-presentation/

..
    https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.is_strongly_connected.html#networkx.algorithms.components.is_strongly_connected
    

.. |Coveralls| image:: https://coveralls.io/repos/github/compassinformatics/wayfarer/badge.svg?branch=main
    :target: https://coveralls.io/github/compassinformatics/wayfarer?branch=main

Demo Services
-------------
virtualenv C:\VirtualEnvs\wayfarer
C:\VirtualEnvs\wayfarer\Scripts\activate.ps1

git clone https://github.com/compassinformatics/wayfarer

cd H:\Temp\wayfarer
pip install wayfarer
pip install -r requirements.demo.txt
Copy-Item -Path demo -Destination C:\VirtualEnvs\wayfarer -Recurse
Copy-Item -Path data -Destination C:\VirtualEnvs\wayfarer -Recurse
cd C:\VirtualEnvs\wayfarer\demo
uvicorn main:app --workers 8 --port 8001