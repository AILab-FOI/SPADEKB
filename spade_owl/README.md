To launch the application, execute mas_launcher.py and then, load in a browser the address of 
the launcher agent web server: http://localhost:33000/launcher

This interface has two columns, the right one allows to generate GraphML files. The left one allows to select a file
describing a graph (in pajek or GraphML formats) and give the IRI of the ontology to use by the MAS. Then, it creates
as much agents as nodes have the graph, and these agents know each oder according to the edges indicated in the graph.
As told above, the idea is the agents to know the loaded ontology, but it fails in the loading of it.
