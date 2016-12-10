import random
import numpy as np
import math
import copy


class CascadeAlgorithm():
    def __init__(self, edges, sources, sinks, min_biomass, given_eat_rates=None):
        self.edges = edges
        self.sources = sources
        self.sinks = sinks
        self.min_biomass = min_biomass
        self.nodelist = []
        for node1, node2 in self.edges:
            if node1 not in self.nodelist:
                self.nodelist.append(node1)
            if node2 not in self.nodelist:
                self.nodelist.append(node2)
        sink_edges = {edge: self.edges[edge] for edge in self.edges if edge[1] in self.sinks}
        self.edges = {edge: self.edges[edge] for edge in self.edges if edge[1] not in self.sinks}
        self.biomass = {}
        self.sink_props = None
        for node in self.nodelist:
            self.update_biomass(node, False)
        self.sink_props = {edge: sink_edges[edge] * 1.0 / self.biomass[edge[0]] for edge in sink_edges}
        self.output_props = {node: (self.get_nonsink_output(node) * 1.0 / self.get_input(
            node) if node not in self.sources and node not in self.sinks else 1) for node in self.nodelist}
        print self.sink_props
        # for node in self.nodelist:
        #   self.update_biomass(node)
        print self.biomass
        print self.output_props
        self.eat_rates = {}
        # self.update_eat_rates()
        i
        self.turn_eat_rates()
        print self.sink_props
        print self.biomass
        print self.eat_rates
        print ""

    def update_biomass(self, node, include_sinks=True):
        if node in self.sources:
            self.biomass[node] = self.sources[node] - sum([self.edges[edge] for edge in self.edges if edge[0] == node])
        else:
            if node in self.biomass and self.biomass[node] == 0 and node not in self.sinks:
                for edge in self.sink_props:
                    if edge[0] == node:
                        self.edges[edge] = 0
                return
            self.biomass[node] = max(0, (self.get_input(node) - self.get_nonsink_output(node)))
            if include_sinks:
                full_biomass = self.biomass[node]
                for edge in self.sink_props:
                    if node == edge[0]:
                        self.biomass[node] -= full_biomass * self.sink_props[edge]
                        self.edges[(node, edge[1])] = full_biomass * self.sink_props[edge]
            if self.biomass[node] < self.min_biomass and node not in self.sinks:
                self.biomass[node] = 0

    def update_eat_rates(self):
        for prey in self.nodelist:
            if prey in self.sinks:
                continue
            elif prey in self.sources:
                for predator in self.get_predators(prey):
                    self.eat_rates[(prey, predator)] = self.edges[(prey, predator)] * 1.0 / self.biomass[predator]
            else:
                predators = []
                for edge in self.edges:
                    if edge[0] == prey and edge[1] not in self.sinks:
                        predators.append(edge[1])
                if len(predators) == 0:
                    continue
                pred_rates = {predator: 0 for predator in predators}
                desired_edges = {predator: self.edges[(prey, predator)] for predator in predators}
                new_edges = self.get_new_edge_weights(prey, predators, self.get_available_output(prey), pred_rates)
                while True:
                    changed = False
                    for predator in predators:
                        new_edges = self.get_new_edge_weights(prey, predators, self.get_available_output(prey),
                                                              pred_rates)
                        # print pred_rates,new_edges,desired_edges
                        if new_edges[predator] < desired_edges[predator] - 0.1:
                            changed = True
                            pred_rates[predator] += 0.00001 * (desired_edges[predator] - new_edges[predator])
                        elif new_edges[predator] > desired_edges[predator] + 0.1:
                            changed = True
                            pred_rates[predator] += 0.00001 * (desired_edges[predator] - new_edges[predator])
                    if not changed:
                        break
                for predator in pred_rates:
                    self.eat_rates[(prey, predator)] = pred_rates[predator]

    # def update_eat_rates(self):
    #   for edge,mass in self.edges.iteritems():
    #     if edge[0] not in self.sources:
    #       pred_rate = 0
    #       new_mass = self.get_new_edge(edge,self.biomass[edge[0]]+self.edges[edge],pred_rate)
    #       prev_values = []
    #       while abs(new_mass-mass) > 0.000001:
    #         if new_mass > mass:
    #           pred_rate-=0.000001
    #         else:
    #           pred_rate+=0.000001
    #         new_mass = self.get_new_edge(edge,self.biomass[edge[0]]+self.edges[edge],pred_rate)
    #         if new_mass in prev_values:
    #           break
    #         else:
    #           prev_values.append(new_mass)
    #       self.eat_rates[edge] = pred_rate
    #     else:
    #       self.eat_rates[edge] = mass*1.0/self.biomass[edge[1]]

    # def update_eat_rates(self):
    #   for edge,mass in self.edges.iteritems():
    #     if edge[0] not in self.sources:
    #       self.eat_rates[edge] = mass*1.0/(self.biomass[edge[0]])/self.biomass[edge[1]]
    #     else:
    #       self.eat_rates[edge] = mass*1.0/self.biomass[edge[1]]

    def turn_eat_rates(self):
        for node in self.nodelist:
            self.update_biomass(node)
        self.biomass[0] = 0
        self.biomass[4] = 0
        desired_biomass = copy.deepcopy(self.biomass)
        print desired_biomass
        print self.sink_props
        exit()
        for edge in self.edges:
            self.eat_rates[edge] = 0
        while True:
            old_biomass = copy.deepcopy(self.biomass)
            mass_flow = self.turns(0, self.biomass[0])
            max_diff = 0
            for edge in self.eat_rates:
                prev_rate = self.eat_rates[edge]
                if edge[1] in self.sinks:
                    self.eat_rates[edge] += 0.00001 * (self.edges[edge] / 1000.0 - mass_flow[edge] / 1000.0)
                else:
                    self.eat_rates[edge] -= 0.00001 * (self.biomass[edge[1]] - desired_biomass[edge[1]])
                    self.eat_rates[edge] += 0.00001 * (self.biomass[edge[0]] - desired_biomass[edge[0]])
                self.eat_rates[edge] = max(0, self.eat_rates[edge])
                max_diff = max(max_diff, abs(self.eat_rates[edge] - prev_rate))
            print mass_flow
            self.biomass = old_biomass
            if max_diff < 0.0000001:
                break
        print self.eat_rates

    def turns(self, event_node, new_mass, iters=1000):
        self.biomass[event_node] = new_mass
        mass_flow = {edge: 0 for edge in self.edges}
        for iter in range(iters):
            new_biomass = copy.deepcopy(self.biomass)
            # print self.biomass
            for node in self.nodelist:
                # print node, self.biomass[node]
                if node in self.sources:
                    new_biomass[node] += 1
                    continue
                if node in self.sinks:
                    for prey in self.get_prey(node):
                        intake = min(self.biomass[prey], self.eat_rates[(prey, node)] * self.biomass[prey])
                        new_biomass[prey] -= intake
                        new_biomass[node] += intake
                        mass_flow[(prey, node)] += intake
                    continue
                for mass_unit in range(int(self.biomass[node])):
                    for prey in self.get_prey(node):
                        if prey in self.sources:
                            intake = min(self.biomass[prey], self.eat_rates[(prey, node)])
                        else:
                            intake = min(self.biomass[prey], self.biomass[prey] * self.eat_rates[(prey, node)])
                        new_biomass[prey] -= intake
                        new_biomass[node] += intake
                        mass_flow[(prey, node)] += intake
            self.biomass = new_biomass
        print self.biomass
        return mass_flow
        # print chosen_node, self.biomass

    def iterative(self, event_node, new_mass):
        self.biomass[event_node] = new_mass
        for prey in self.get_prey(event_node):
            self.update_edges_from_weights(prey, self.get_new_edge_weights(prey, self.get_predators(prey),
                                                                           self.get_available_output(prey)))
            self.update_biomass(prey)
        for node in self.nodelist:
            self.update_biomass(node)
        print self.biomass, self.edges
        while True:
            permut = list(self.nodelist)
            random.shuffle(permut)
            prev_biomass = dict(self.biomass)
            prev_edges = dict(self.edges)
            for prey in permut:
                if prey in self.sinks:
                    self.update_biomass(prey)
                    continue
                self.update_edges_from_weights(prey, self.get_new_edge_weights(prey, self.get_predators(prey),
                                                                               self.get_available_output(prey)))
                self.update_biomass(prey)
                print prey, self.biomass, self.edges
            max_diff = 0
            for node in self.nodelist:
                max_diff = max([abs(self.biomass[node] - prev_biomass[node]), max_diff])
            for edge in self.edges:
                max_diff = max([abs(self.edges[edge] - prev_edges[edge]), max_diff])
            if max_diff < 1:
                break
        print self.biomass, self.edges

    def update_edges_from_weights(self, prey, pred_weights):
        for predator in pred_weights:
            self.edges[(prey, predator)] = pred_weights[predator]

    def get_predators(self, node):
        return [predator for (prey, predator) in self.edges if prey == node and predator not in self.sinks]

    def return_sink_biomass(self, node):
        sum_props = 0
        for edge in self.sink_props:
            if edge[0] == node:
                sum_props += self.sink_props[edge]
        self.biomass[node] /= (1 - sum_props)

    def get_presink_biomass(self, node):
        sum_props = 0
        for edge in self.sink_props:
            if edge[0] == node:
                sum_props += self.sink_props[edge]
        return self.biomass[node] / (1 - sum_props)

    def get_prey(self, node):
        return [prey for (prey, predator) in self.edges if predator == node]

    def get_input(self, node):
        return sum([self.edges[edge] for edge in self.edges if edge[1] == node])

    def get_available_output(self, node):
        # if node==2:
        #  print self.biomass[node],self.get_presink_biomass(node),self.get_presink_biomass(node)*self.output_props[node]
        return self.get_input(node)  # *self.output_props[node]

    def get_nonsink_output(self, node):
        return sum([self.edges[edge] for edge in self.edges if edge[0] == node and edge[1] not in self.sinks])

    def get_output(self, node):
        return sum([self.edges[edge] for edge in self.edges if edge[0] == node])

    def get_inout_diff(self, node, edges):
        return sum([edges[edge] for edge in edges if edge[1] == node]) - sum(
            [edges[edge] for edge in edges if edge[0] == node])

    # def get_isolated_edge_weight(self,prey,predator,prey_biomass):
    #   if prey in self.sources:
    #     return min(self.biomass[prey]+self.edges[(prey,predator)],self.biomass[predator] * self.eat_rates[(prey,predator)])
    #   temp_prey = prey_biomass
    #   new_edge = 0
    #   for i in range(int(self.biomass[predator])):
    #     new_edge += temp_prey * self.eat_rates[(prey,predator)]
    #     temp_prey -= temp_prey * self.eat_rates[(prey,predator)]
    #   return max(0,new_edge)

    def get_new_edge_weights(self, prey, predators, prey_biomass, rates=None, ratio=1):
        if len(predators) == 0:
            return {}
        if rates is None:
            rates = {predator: self.eat_rates[(prey, predator)] for predator in predators if predator not in self.sinks}
        if prey in self.sources:
            desires = {predator: self.biomass[predator] * self.eat_rates[(prey, predator)] for predator in predators}
            if sum(desires.values()) <= self.sources[prey]:
                return desires
            else:
                desires_nor = {predator: desires[predator] * 1.0 / sum(desires.values()) * self.sources[prey] for
                               predator in desires}
                return desires_nor
        temp_prey = prey_biomass
        new_edges = {predator: 0 for predator in predators}
        predator_masses = {predator: 1.0 * self.get_presink_biomass(predator) * ratio for predator in predators}
        predator_masses = {predator: mass for predator, mass in predator_masses.iteritems() if mass > 0}
        if len(predator_masses) == 0 or prey_biomass == 0 or self.biomass[prey] == 0:
            return new_edges
        p_masses_nor = {predator: mass / min(predator_masses.values()) for predator, mass in
                        predator_masses.iteritems()}
        for i in range(int(min(predator_masses.values()))):
            p_items = p_masses_nor.items()
            random.shuffle(p_items)
            for predator, mass in p_items:
                new_edges[predator] += temp_prey * mass * rates[predator]
                temp_prey -= temp_prey * mass * rates[predator]
        combined_edges = {edge: self.edges[(prey, edge)] * (1 - ratio) + new_edges[edge] for edge in new_edges}
        return combined_edges

        # def get_new_edge(self,edge,prey_biomass,rate=None):
        #   if rate is None:
        #     rate = self.eat_rates[edge]
        #   if edge[0] in self.sources:
        #     return min(self.biomass[edge[0]]+self.edges[edge],self.biomass[edge[1]] * rate)
        #   temp_prey = prey_biomass
        #   new_edge = 0
        #   for i in range(int(self.biomass[edge[1]])):
        #     new_edge += temp_prey * rate
        #     temp_prey -= temp_prey * rate
        #   return max(0,new_edge)

        # def cascade(self,event_node,new_mass):
        #   changed_prey = []
        #   changed_predators = []
        #   self.biomass[event_node] = new_mass
        #   for edge in self.edges:
        #     if event_node == edge[1]:
        #       self.update_edge(edge)
        #       changed_prey.append(edge[0])
        #     elif event_node == edge[0]:
        #       changed_predators.append(edge[1])
        #   print self.biomass
        #   while len(changed_prey) + len(changed_predators) > 0:
        #     if len(changed_predators) > 0:
        #       changed_node = changed_predators[0]
        #       del changed_predators[0]
        #     else:
        #       changed_node = changed_prey[0]
        #       del changed_prey[0]
        #     print changed_node
        #     if self.biomass[changed_node] == 0:
        #       continue
        #     prey_to_change = []
        #     predators_to_change = []
        #     for edge in self.edges:
        #       if changed_node == edge[1]:
        #         if self.biomass[edge[0]] != 1:
        #           self.edges[edge] = (1-capture_rate)*self.edges[edge]+ capture_rate * self.biomass[edge[0]] * self.biomass[edge[1]] * self.eat_rates[edge]
        #         else:
        #           self.edges[edge] = min(2000,self.biomass[edge[0]] * self.biomass[edge[1]] * self.eat_rates[edge])
        #           print self.edges[edge]
        #         if edge[0] not in changed_prey:
        #           prey_to_change.append(edge[0])
        #       elif changed_node == edge[0] and edge[1] not in changed_predators:
        #         predators_to_change.append(edge[1])
        #     random.shuffle(prey_to_change)
        #     random.shuffle(predators_to_change)
        #     changed_prey += prey_to_change
        #     changed_predators += predators_to_change
        #     self.update_biomass(changed_node)
        #     print self.biomass


class TurnAlgorithm():
    def __init__(self, masses, edges, sources, sinks, piles, min_biomass):
        self.default_biomass = masses
        self.edges = edges
        self.sources = sources
        self.sinks = sinks
        self.piles = piles
        self.min_biomass = min_biomass
        self.nodelist = []
        for node1, node2 in self.edges:
            if node1 not in self.nodelist:
                self.nodelist.append(node1)
            if node2 not in self.nodelist:
                self.nodelist.append(node2)
        self.edges = {edge: self.edges[edge] for edge in self.edges}
        self.biomass = copy.deepcopy(masses)
        sink_edges = {edge: self.edges[edge] for edge in self.edges if edge[1] in self.sinks}
        self.sink_edge_per_input = {edge: self.edges[edge] * 1.0 / sum(sink_edges.values()) for edge in sink_edges}
        self.edge_per_input = {edge: self.edges[edge]*1.0 / max(self.edges.values()) for edge in self.edges}
        self.calc_eat_rates()

    def reset(self):
        self.biomass = copy.deepcopy(self.default_biomass)

    def calc_eat_rates(self):
        self.eat_rates = {}
        for edge in self.edges:
            if edge[1] in self.sinks or edge[1] in self.piles:
                self.eat_rates[edge] = self.edge_per_input[edge]/(self.biomass[edge[0]] if self.biomass[edge[0]]>0 else 1)
            elif edge[0] in self.sources:
                self.eat_rates[edge] = self.edge_per_input[edge]/self.biomass[edge[1]]
            else:
                self.eat_rates[edge] = self.edge_per_input[edge]/self.biomass[edge[1]]/self.biomass[edge[0]]


    def turn_eat_rates(self,verbose=False):
        for edge in self.edges:
            self.eat_rates[edge] = 0
        while True:
            old_biomass = copy.deepcopy(self.biomass)
            mass_flow, average_masses = self.turns(0, self.biomass[0], iters=self.train_iters)
            max_diff = 0
            for edge in self.eat_rates:
                delta = (self.edge_per_input[edge] - mass_flow[edge] * 1.0 / self.train_iters)
                max_diff = max(delta,max_diff)
                self.eat_rates[edge] += self.learn_rate * delta
                self.eat_rates[edge] = max(0, self.eat_rates[edge])
            if max_diff < self.learn_thresh:
                self.biomass = old_biomass
                break
            if verbose:
                print self.biomass, mass_flow
            self.biomass = old_biomass

    def turns(self, event_node, new_mass, iters=1000, verbose=False):
        self.biomass[event_node] = new_mass
        mass_flow = {edge: 0 for edge in self.edges}
        average_masses = {node: 0 for node in self.nodelist}
        for iter in range(iters):
            for node in self.sources:
                self.biomass[node]+=1.0
            new_biomass = copy.deepcopy(self.biomass)
            for node in self.nodelist:
                if node in self.sources:
                    continue
                if node in self.sinks or node in self.piles:
                    for prey in self.get_prey(node):
                        intake = min(self.biomass[prey], self.eat_rates[(prey, node)] * self.biomass[prey])
                        new_biomass[prey] -= intake
                        if new_biomass[prey] < 0:
                            new_biomass[prey] = 0
                        new_biomass[node] += intake
                        mass_flow[(prey, node)] += intake
                    continue
                for prey in self.get_prey(node):
                    if prey in self.sources:
                        intake = min(self.biomass[prey], self.eat_rates[(prey, node)] * self.biomass[node])
                    else:
                        intake = min(self.biomass[prey], self.biomass[prey] * self.eat_rates[(prey, node)] * self.biomass[node])
                    new_biomass[prey] -= intake
                    if new_biomass[prey] < 0:
                        new_biomass[prey] = 0
                    new_biomass[node] += intake
                    mass_flow[(prey, node)] += intake
            self.biomass = new_biomass
            for node in self.biomass:
                if self.biomass[node] < self.min_biomass and node not in self.sinks and node not in self.sources:
                    self.biomass[node] = 0
                average_masses[node] += self.biomass[node] * 1.0 / iters
            if verbose:
                print self.biomass
        return mass_flow, average_masses

    def get_predators(self, node):
        return [predator for (prey, predator) in self.edges if prey == node and predator not in self.sinks]

    def get_prey(self, node):
        return [prey for (prey, predator) in self.edges if predator == node]

    def get_input(self, node):
        return sum([self.edges[edge] for edge in self.edges if edge[1] == node])

    def get_output(self, node):
        return sum([self.edges[edge] for edge in self.edges if edge[0] == node])



