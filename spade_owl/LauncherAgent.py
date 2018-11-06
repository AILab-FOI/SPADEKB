import asyncio
import math

import names # random name generator

import numpy as np
import onto2nx

from aiohttp import web

import networkx as nx
from bokeh.models import ColumnDataSource, HoverTool, TapTool
from bokeh.plotting import figure
from spade.template import Template

from NodeAgent import NodeAgent

from spade.behaviour import FSMBehaviour
from spade.behaviour import State

from spade_owl import SpadeOWLAbstractAgent, RecvBehav


class LauncherAgent(SpadeOWLAbstractAgent):

    # def get_global_utility_at(self, x, avail_contacts):
    #     sum_util = 0
    #     for id_ag, msg_dict in avail_contacts.items():
    #         if msg_dict:
    #             sum_util += self.get_local_utility_at(x, msg_dict['x0'], msg_dict['w'])
    #     return sum_util
    #
    # def get_local_utility_at(self, x, x0, w):
    #     return math.exp(-0.5 * math.pow((x - x0) / (w), 2))

    async def load_graph(self, graph_data, onto_uri, graph_file_type):
        # Load the graph file
        if graph_file_type == 'pajek':
            nxGraph = nx.read_pajek(graph_data.file)
        elif graph_file_type == 'graphml':
            nxGraph = nx.read_graphml(graph_data.file)

        self.subgraph = nxGraph
        self.bel_graph = onto2nx.parse_owl_rdf(onto_uri)

        # Calculate the number of nodes in the graph
        nodes_list = list(nxGraph.nodes(data=True))

        # Calculate epsilon
        # degree_sequence = [d for n, d in nxGraph.degree()]

        # For each agent in the graph
        i = 0

        template = Template()
        template.set_metadata('conversation', 'consensus')
        self.add_behaviour(RecvBehav(), template)
        self.add_behaviour(self.ConsensusObserver())

        for key, node in nodes_list:
            # Create an agent
            if 'id' not in node:
                node['id'] = node['name']
            jid1 = "".join(node['id'].split()).lower() + self.jid_domain

            # print("Name: ", jid1)

            passwd1 = "test"

            # Give the agent a name, that has the same label as in the graph
            node_agent = NodeAgent(jid1, password=passwd1, onto_uri=onto_uri, use_container=True, loop=self.loop)

            self.mas_dict[jid1] = node_agent
            base_port = 30000
            url = node_agent.url + str(base_port + i) + "/agent"
            nxGraph.node[key]['url'] = url

            neighList = list(nxGraph.neighbors(key))
            neighList.append(key)
            # print("NeighList: ", neighList)
            subgraph = nxGraph.subgraph(neighList)

            config = {'base_port':base_port, 'value': i, 'subgraph': subgraph, 'observers': [self.jid]}
            config.update(node)
            node_agent.configure(config)

            i = i + 1

        coros = [agent.deploy() for agent in self.mas_dict.values()]
        await asyncio.gather(*coros)

        await self.subscribe_to_neighbours()

        # calculate avail_contacts
        await self.update_available_contacts()

    async def get_file_controller(self, request):
        # WARNING: don't do that if you plan to receive large files!
        data = await request.post()

        if 'stopMAS' in data:
            self.stop_mas()
            raise web.HTTPFound('/launcher')
        else:
            graph_file_data = data['graphInputFile']
            await self.load_graph(graph_file_data, data['OWLURI'], data['graphFileType'])

            raise web.HTTPFound('/agent')

    async def generate_graph_file(self, request):
        # WARNING: don't do that if you plan to receive large files!
        data = await request.post()

        nodesNumber = int(data['nodesNumber'])

        if data['graphGenerator'] == 'complete':
            nxOutputGraph = nx.complete_graph(nodesNumber)
        elif data['graphGenerator'] == "cycle":
            nxOutputGraph = nx.cycle_graph(nodesNumber)
        elif data['graphGenerator'] == "wheel":
            nxOutputGraph = nx.wheel_graph(nodesNumber)
        elif data['graphGenerator'] == "star":
            nxOutputGraph = nx.star_graph(nodesNumber)
        elif data['graphGenerator'] == "random":
            prob = float(data['probability'])
            nxOutputGraph = nx.erdos_renyi_graph(nodesNumber, prob)
        elif data['graphGenerator'] == "watts":
            prob = float(data['probability'])
            k = int(data['neighDist']) # neighbours distance
            nxOutputGraph = nx.watts_strogatz_graph(nodesNumber, k, prob)
        elif data['graphGenerator'] == "barabasi":
            m = int(data['edgesNew']) # number of edges to attach a new node
            nxOutputGraph = nx.barabasi_albert_graph(nodesNumber, m)
        elif data['graphGenerator'] == "geometric":
            radius = float(data['radius']) # distance threshold value
            nxOutputGraph = nx.random_geometric_graph(nodesNumber, radius)

        # writing gml file
        with open('{}.gml'.format(data['graphOutputFile']), 'w') as f:
            # Header of graphml file
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" ')
            f.write('xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.1/graphml.xsd\">\n')
            f.write('<key id = "name" for ="node" attr.name="name" attr.type="string" />\n')
            f.write('<key id = "lim_inf" for ="node" attr.name="lim_inf" attr.type="float" />\n')
            f.write('<key id = "lim_sup" for ="node" attr.name="lim_sup" attr.type="float" />\n')
            f.write('<key id = "x0" for ="node" attr.name="x0" attr.type="float" />\n')
            f.write('<key id = "w" for ="node" attr.name="w" attr.type="float" />\n')
            f.write('<graph id = "G" edgedefault = "undirected">\n')
            i = 0
            # Writing nodes
            if data['nodeWeight'] == "same":
                weight = np.random.random()
            for node in nxOutputGraph.nodes():
                f.write('<node id="{}">\n'.format(i))
                f.write('<data key="name">{}</data>\n'.format("".join(names.get_full_name().split())))
                new_node_value = np.random.random()
                rangeSize = float(data['rangeSize'])
                if data['initialCentered'] == 'yes':
                    porc_range = 0.5
                else: porc_range = np.random.random()
                f.write('<data key="lim_inf">{}</data>\n'.format(new_node_value - porc_range * rangeSize))
                f.write('<data key="lim_sup">{}</data>\n'.format(new_node_value + porc_range * rangeSize))
                f.write('<data key="x0">{}</data>\n'.format(new_node_value))
                if data['nodeWeight'] == "different":
                    weight = np.random.random()
                f.write('<data key="w">{}</data>\n'.format(weight))
                f.write('</node>\n')
                i = i + 1

            # Writing edges
            for (u, v) in nxOutputGraph.edges():
                f.write('<edge id="{}" source="{}" target="{}" label="knows"></edge>\n'.format(i, u, v))
                i = i + 1

            f.write('</graph>\n')
            f.write('</graphml>')

        raise web.HTTPFound('/launcher')


    class ConsensusObserver(FSMBehaviour):
        def setup(self):
            class ReceiveState(State):
                async def run(self):
                    sender_waiting = {key: value for key, value in self.agent.avail_contacts.items() if value is None}
                    if sender_waiting:
                        # print("Still not received all the messages: ", sender_waiting)
                        self.set_next_state("Receive")
                    else:
                        # print("Received all messages of this iteration")
                        self.set_next_state("Update")

            class UpdateState(State):
                async def run(self):

                    # self.agent.iter = self.agent.iter + 1

                    self.agent.avail_contacts = {key: None for key, value in self.agent.presence.get_contacts().items()
                                                 if 'presence' in value and value['presence'].show is not None}

                    # print("Avail_contacts: ", self.agent.avail_contacts)

                    self.set_next_state("Receive")

            class StopState(State):
                async def run(self):
                    self.kill()

            self.add_state("Receive", ReceiveState(), initial=True)
            self.add_state("Update", UpdateState())
            self.add_state("Stop", StopState())
            self.add_transition("Receive", "Receive")
            self.add_transition("Receive", "Update")
            self.add_transition("Update", "Receive")
            self.add_transition("Update", "Stop")

    def plot_create_global_utility(self, doc):
        self.plot_utility = figure(x_axis_label='X', title="Utility Evolution")

        self.source_global_utility = ColumnDataSource(dict(util_line_x=[], util_line_y=[]))
        self.plot_utility.line(x='util_line_x', y='util_line_y', source=self.source_global_utility )

        self.source_utility = ColumnDataSource(dict(x_values=[], utilities=[], id=[], w=[]))
        self.plot_utility.circle(size=10, fill_color='#e2d876', x='x_values', y='utilities', source=self.source_utility)

        self.plot_utility.add_tools(HoverTool(tooltips=[("id", "@id"), ("w", "@w")]), TapTool())

        doc.add_periodic_callback(self.plot_update_global_utility, period_milliseconds=500)
        doc.add_root(self.plot_utility)

    # def plot_update_global_utility(self):
    #     # with self.mutex:
    #     if self.rugosity != None:
    #         self.plot_utility.title.text = "Utility Evolution - Roughness = " + str(self.rugosity)
    #
    #     new_source_utility = dict(x_values=self.sum_value, utilities=self.utility, id=self.ids, w=self.ws)
    #     self.source_utility.data.update(new_source_utility)
    #
    #     new_source_utility = dict(util_line_x=self.coord_x, util_line_y=self.gutility)
    #     self.source_global_utility.data.update(new_source_utility)
    #
    # def plots_to_add(self):
    #     super().plots_to_add()
    #
    #     self.bokeh_server.add_plot("/bkutil", self.plot_create_global_utility)

    def stop_mas(self):
        for _, node in self.mas_dict.items():
            node.stop()
        print("Agents finished")

    def stop(self):
        self.stop_mas()

        super().stop()

    def setup(self):
        # self.logger = logging.getLogger("[{}]".format(self.name))
        self.mas_dict = {}
        self.ids = []

        self.web.add_get("/launcher", lambda request: {}, "launcher.html")
        self.web.add_post("/submit", self.get_file_controller, None)
        self.web.add_post("/submit_graph", self.generate_graph_file, None)
        super().setup()
