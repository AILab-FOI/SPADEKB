import json
from abc import ABCMeta

try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")

from threading import Lock
from asyncio import Lock as aioLock

import networkx as nx

from bokeh.models import ColumnDataSource, from_networkx, Circle, MultiLine, NodesAndLinkedEdges, LabelSet, HoverTool, \
    TapTool, OpenURL
from bokeh.plotting import figure

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import spade_bokeh as spBokeh

import owlready2 as owl
import onto2nx as onto2nx


class SpadeOWLAbstractAgent(spBokeh.BokehServerMixin, Agent, metaclass=ABCMeta):
    def __init__(self, *args, onto_uri= None, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = None
        self.subgraph = None
        self.bel_graph = None
        self.url = "localhost:"
        self.jid_domain = "@gtirouter.dsic.upv.es"
        self.presence.approve_all = True

        self.source = ColumnDataSource(dict(iterations=[], values=[]))

        self.new_data = dict(iterations=[], values=[])
        self.avail_contacts = {}
        self.avail_observers = []

        self.onto_uri = onto_uri
        if onto_uri != None:
            self.onto = owl.get_ontology(onto_uri).load()
            print("Ontology: ", onto_uri)
            # self.bel_graph = nx.Graph()

            self.bel_graph = onto2nx.parse_owl_rdf(onto_uri)

            # for node in self.onto.classes():
            #    self.bel_graph.add_node(node)


            # self.bel_graph.add_nodes_from(list(self.onto.classes()))
            print("Belief graph created from: ", list(self.onto.classes()))
            print("Node: ", self.bel_graph.nodes())

        self.avail_mutex = aioLock()

    async def get_neighbours(self):
        for key, node in list(self.subgraph.nodes(data=True)):
            jid1 = node['id'].lower() + self.jid_domain
            if jid1 != str(self.jid):
                yield jid1

    async def subscribe_to_neighbours(self):
        # each node is subscribed to its neighbors
        async for neighbor in self.get_neighbours():
            self.presence.subscribe(neighbor)

    async def update_available_contacts(self):
        contacts = self.presence.get_contacts()
        async with self.avail_mutex:
            self.avail_contacts = {key: None for key, value in contacts.items() if
                                   'presence' in value and value['presence'].show is not None}

    async def agent_web_controller(self, request):
        n = len(self.avail_contacts.items())
        sNeig = []
        lNeig = []
        i = 1
        sNeig.append({"name": str(self.jid.bare())})
        for node in self.avail_contacts.keys():
            sNeig.append({"name": str(node.bare())})
            lNeig.append({"source": 0, "target": i})
            i = i + 1

        bokehGraph = self.bokeh_server.get_plot_script("/bkappgraph/")
        # script = self.bokeh_server.get_plot_script("/bkapp/")
        beliefs = self.bokeh_server.get_plot_script("/bkbel/")

        return {"graphBokeh": bokehGraph, "beliefBokeh": beliefs}

    def plot_create(self, doc):
         plot = figure(x_range=(-1.1, 1.1), y_range=(-1.1, 1.1), title="Belief Graph")
         plot.axis.visible = False

         # node_labels = nx.get_node_attributes(self.bel_graph, 'id')
         # node_labels = tuple([label for label in node_labels.values()])
         node_labels = list(self.bel_graph.node.keys())

         ncolor = ['#2b83ba' for name in node_labels]
         nsize = [10 for name in node_labels]

         graph = from_networkx(self.bel_graph, nx.shell_layout, scale=1, center=(0, 0))

         graph.node_renderer.glyph = Circle(size='nsize', fill_color='ncolor')
         graph.node_renderer.selection_glyph = Circle(size='nsize', fill_color='#054872')
         graph.node_renderer.hover_glyph = Circle(size='nsize', fill_color='#abdda4')
         graph.name = "bel_graph"

         graph.node_renderer.data_source.data.update(dict(id=node_labels, ncolor=ncolor, nsize=nsize))

         graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=2)
         graph.edge_renderer.selection_glyph = MultiLine(line_color='#054872', line_width=2)
         graph.edge_renderer.hover_glyph = MultiLine(line_color='#abdda4', line_width=2)

         graph.selection_policy = NodesAndLinkedEdges()
         # graph.inspection_policy = EdgesAndLinkedNodes()

         plot.renderers.append(graph)

         x, y = zip(*graph.layout_provider.graph_layout.values())

         source_graph = ColumnDataSource(data=dict(x=x, y=y, id=node_labels))
         labels = LabelSet(x='x', y='y', text='id', source=source_graph)

         plot.renderers.append(labels)

         # add tools to the plot
         plot.add_tools(HoverTool(names=["bel_graph"]), TapTool())

         doc.add_root(plot)

    def plot_create_graph(self, doc):
        if self.subgraph:
            plot = figure(x_range=(-1.1, 1.1), y_range=(-1.1, 1.1))
            plot.axis.visible = False

            node_labels = nx.get_node_attributes(self.subgraph, 'id')
            node_labels = tuple([label for label in node_labels.values()])
            node_urls = nx.get_node_attributes(self.subgraph, 'url')
            node_urls = tuple([value for value in node_urls.values()])
            node_lim_inf = nx.get_node_attributes(self.subgraph, 'lim_inf')
            node_lim_inf = tuple([value for value in node_lim_inf.values()])
            node_lim_sup = nx.get_node_attributes(self.subgraph, 'lim_sup')
            node_lim_sup = tuple([value for value in node_lim_sup.values()])
            ncolor = ['#2b83ba' for name in node_labels]
            nsize = [15 for name in node_labels]
            if self.name != 'launcher':
                node_labels_low = [name.lower() for name in node_labels]
                ncolor[node_labels_low.index(self.name)] = '#ff0202'
                nsize[node_labels_low.index(self.name)] = 25

            graph = from_networkx(self.subgraph, nx.spring_layout, scale=1, center=(0, 0))

            graph.node_renderer.glyph = Circle(size='nsize', fill_color='ncolor')
            graph.node_renderer.selection_glyph = Circle(size='nsize', fill_color='#054872')
            graph.node_renderer.hover_glyph = Circle(size='nsize', fill_color='#abdda4')
            graph.name = "graph"

            graph.node_renderer.data_source.data.update(dict(id=node_labels, url=node_urls, inf=node_lim_inf,
                                                             sup=node_lim_sup, ncolor=ncolor, nsize=nsize))

            graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
            graph.edge_renderer.selection_glyph = MultiLine(line_color='#054872', line_width=5)
            graph.edge_renderer.hover_glyph = MultiLine(line_color='#abdda4', line_width=5)

            graph.selection_policy = NodesAndLinkedEdges()
            # graph.inspection_policy = EdgesAndLinkedNodes()

            plot.renderers.append(graph)

            x, y = zip(*graph.layout_provider.graph_layout.values())

            source_graph = ColumnDataSource(data=dict(x=x, y=y, id=node_labels, url=node_urls))
            labels = LabelSet(x='x', y='y', text='id', source=source_graph)

            plot.renderers.append(labels)

            # add tools to the plot
            plot.add_tools(HoverTool(tooltips=[("url", "@url"), ("range", "[@inf, @sup]")], names=["graph"]), TapTool())

            url = "http://@url"
            taptool = plot.select(type=TapTool)
            taptool.callback = OpenURL(url=url)

            doc.add_root(plot)

    # def plot_update(self):
    #     with self.mutex:
    #         if self.new_data["iterations"]:
    #             self.source.stream(self.new_data)
    #             for i in range(len(self.new_data["iterations"])):
    #                 self.new_data['iterations'][i] = [self.new_data["iterations"][i][-1]]
    #                 self.new_data['values'][i] = [self.new_data["values"][i][-1]]

    def stop(self):
        print("Stopping agent ", self.jid.bare())

        contacts = self.presence.get_contacts()
        avail_contacts = {key: value for key, value in contacts.items() if
                          'presence' in value and value['presence'].show is not None}

        for key in avail_contacts:
            if (key.bare() != self.jid.bare()):
                # print(" --Neighbor: ", key.bare())
                self.presence.unsubscribe(str(key))

        self.bokeh_server.stop()

        super().stop()

    def plots_to_add(self):
        self.bokeh_server.add_plot("/bkappgraph", self.plot_create_graph)
        self.bokeh_server.add_plot("/bkbel", self.plot_create)

    def setup(self):
        # print("Agent {} running".format(self.name))

        self.mutex = Lock()

        self.web.add_get("/agent", self.agent_web_controller, "agent_cons.html")

        self.web.start(port=self.web.port)

        self.plots_to_add()

        self.bokeh_server.start(port=self.port)


class RecvBehav(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10000)  # wait for a message for 10 seconds
        if msg:
            sender = msg.sender.bare()
            async with self.agent.avail_mutex:
                self.agent.avail_contacts[sender] = json.loads(msg.body)  # float(msg.body)
                # print("Received: ", self.agent.avail_contacts[sender])
            # self.agent.logger.error("Received new message: {}".format(self.agent.avail_contacts))