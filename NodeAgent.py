import logging

from spade.template import Template

from spade_owl import SpadeOWLAbstractAgent
# from fsm_consensus_behavior import Consensus


class NodeAgent(SpadeOWLAbstractAgent):

    def configure(self, config):
        self.web.port = config['base_port'] + config['value']
        self.url = self.url + str(self.web.port) + "/agent"
        self.port = self.web.port + 4000
        self.subgraph = config['subgraph']
        self.avail_observers += config['observers']

    # def add_consensus_behaviour(self):
    #     template = Template()
    #     template.set_metadata('conversation', 'scum')
    #
    #     self.add_behaviour(Consensus(), template)

    async def deploy(self):
        await self.async_start(auto_register=True)
        # self.add_consensus_behaviour()

    # def store_iteration_values(self, nAgents, neighbour_diffs):
    #     with self.mutex:
    #         if len(self.new_data["iterations"]) < nAgents:
    #             self.new_data['iterations'] = [[] for _ in range(nAgents)]
    #             self.new_data['values'] = [[] for _ in range(nAgents)]
    #             self.state_x = [[] for _ in range(nAgents)]
    #             self.state_y = [[] for _ in range(nAgents)]
    #
    #         self.new_data["iterations"][0].append(self.iter)
    #         self.new_data["values"][0].append(self.my_value)
    #
    #         self.state_x[0].append(self.iter)
    #         self.state_y[0].append(self.my_value)
    #
    #         for i in range(len(neighbour_diffs)):
    #             self.state_x[i + 1].append(self.iter)
    #             self.new_data["iterations"][i + 1].append(self.iter)
    #             self.state_y[i + 1].append(neighbour_diffs[i] + self.my_value)
    #             self.new_data["values"][i + 1].append(neighbour_diffs[i] + self.my_value)

    def setup(self):
        super().setup()

        # self.logger = logging.getLogger("[{}]".format(self.name))

        self.iter = 0
