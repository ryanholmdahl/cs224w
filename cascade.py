import random
import numpy as np
import math
import copy

class TurnAlgorithm():
    # masses: array, masses[i] = biomass of node i
    # edge_weights: dictionary, edge_weights[(prey,predator)] = biomass flow from prey to predator
    # sources: list of source node ids
    # sinks: list of sink node ids
    # piles: list of pile node ids
    # min_biomass_ratio: if a node's biomass falls below min_biomass_ration*default_mass, then we consider it extinct
    def __init__(self, masses, edge_weights, sources, sinks, piles, min_biomass_ratio):
        self.biomass = np.array(masses)
        self.default_biomass = np.array(masses) # make a separate copy
        self.edge_weights = edge_weights
        self.sources = sources
        self.sinks = sinks
        self.piles = piles
        self.min_biomass_ratio = min_biomass_ratio
        self.edgelist = edge_weights.keys() # list of (prey, predator) tuples

        self.nodelist = []
        for node1, node2 in self.edgelist:
            if node1 not in self.nodelist:
                self.nodelist.append(node1)
            if node2 not in self.nodelist:
                self.nodelist.append(node2)
        self.nodelist = np.array(self.nodelist)
        
        self.max_node_id = max(self.nodelist)
        self.is_pile = np.zeros(self.max_node_id+1, dtype=bool)
        self.is_sink = np.zeros(self.max_node_id+1, dtype=bool)
        self.is_source = np.zeros(self.max_node_id+1, dtype=bool)
        for node in self.nodelist:
            if node in self.piles:
                self.is_pile[node] = True
            elif node in self.sinks:
                self.is_sink[node] = True
            elif node in self.sources:
                self.is_source[node] = True

        max_mass_flow = float(max(self.edge_weights.values()))
        self.normalized_edge_weights = {edge: self.edge_weights[edge] / max_mass_flow for edge in self.edgelist}
        self.calc_eat_rates()

    def reset(self):
        self.biomass = copy.deepcopy(self.default_biomass)

    def calc_eat_rates(self):
        self.eat_rates = np.zeros((self.max_node_id+1,self.max_node_id+1))
        for edge in self.edgelist:
            prey, predator = edge
            # normalized_edge_weights are floats, so no truncation errors here
            if self.is_sink[predator] or self.is_pile[predator]:
                self.eat_rates[edge] = self.normalized_edge_weights[edge]/(self.biomass[prey] if self.biomass[prey]>0 else 1)
            elif self.is_source[prey]:
                self.eat_rates[edge] = self.normalized_edge_weights[edge]/self.biomass[predator]
            else:
                self.eat_rates[edge] = self.normalized_edge_weights[edge]/self.biomass[predator]/self.biomass[prey]

    def turns(self, event_node, new_mass, iters=1000, verbose=False):
        self.biomass[event_node] = new_mass
        mass_flow = np.zeros((self.max_node_id+1,self.max_node_id+1))
        average_masses = np.zeros(self.max_node_id+1)
        # prev_average_masses = np.array(average_masses)

        # create separate variable for computing new_biomass to allow for simultaneous updates
        new_biomass = copy.deepcopy(self.biomass)
        for i in xrange(iters):
            for edge in self.edgelist:
                prey, predator = edge
                if self.is_sink[predator] or self.is_pile[predator]:
                    intake = min(self.biomass[prey], self.eat_rates[edge] * self.biomass[prey])
                    new_biomass[prey] -= intake
                    new_biomass[predator] += intake
                    mass_flow[edge] += intake
                else:
                    if self.is_source[prey]:
                        intake = self.eat_rates[edge] * self.biomass[predator]
                    else:
                        intake = min(self.biomass[prey], self.biomass[prey] * self.eat_rates[edge] * self.biomass[predator])
                        new_biomass[prey] -= intake
                    new_biomass[predator] += intake
                    mass_flow[edge] += intake
            self.biomass = np.maximum(new_biomass, 0) # set self.biomass to new_biomass
            for node in self.nodelist:
                if self.biomass[node] < self.min_biomass_ratio * self.default_biomass[node] and not self.is_sink[node] and not self.is_source[node]:
                    self.biomass[node] = 0
            average_masses = (average_masses * i + self.biomass) / float(i+1)
            if verbose:
                print self.biomass
            # if (i+1)%1000 == 0:
            #     # print average_masses
            #     print np.linalg.norm(average_masses - prev_average_masses)
            # prev_average_masses = np.array(average_masses)
        return mass_flow, average_masses