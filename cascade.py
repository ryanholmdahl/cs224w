__author__ = 'ryhol_000'
import random

class CascadeAlgorithm():
  def __init__(self,edges,sources,sinks,min_biomass):
    self.edges = edges
    self.sources = sources
    self.sinks = sinks
    self.min_biomass = min_biomass
    self.nodelist = []
    for node1,node2 in self.edges:
      if node1 not in self.nodelist:
        self.nodelist.append(node1)
      if node2 not in self.nodelist:
        self.nodelist.append(node2)
    sink_edges = {edge:self.edges[edge] for edge in self.edges if edge[1] in self.sinks}
    self.edges = {edge:self.edges[edge] for edge in self.edges if edge[1] not in self.sinks}
    self.biomass = {}
    self.sink_props = None
    for node in self.nodelist:
      self.update_biomass(node)
    self.sink_props = {node:sum(sink_edges[edge] for edge in sink_edges if node == edge[0])*1.0/self.biomass[node] for node in self.nodelist if node not in self.sinks}
    self.eat_rates = {}
    self.update_eat_rates()
    self.output_props = {node:(self.get_output(node)*1.0/self.biomass[node] if node not in self.sources and node not in self.sinks else 1) for node in self.nodelist}
    print self.sink_props
    print self.output_props

  def update_biomass(self,node):
    if node in self.sources:
      self.biomass[node] = self.sources[node] - sum([self.edges[edge] for edge in self.edges if edge[0] == node])
    elif node in self.sinks:
      self.biomass[node] = 0
    else:
      if node in self.biomass and self.biomass[node] == 0:
        return
      self.biomass[node] = max(0,(self.get_input(node) - self.get_output(node)))
      if self.biomass[node] < self.min_biomass:
        self.biomass[node] = 0

  def update_eat_rates(self):
    for prey in self.nodelist:
      if prey in self.sources:
        for predator in self.get_predators(prey):
          self.eat_rates[(prey,predator)] = self.edges[(prey,predator)]*1.0/self.biomass[predator]
      else:
        predators = []
        for edge in self.edges:
          if edge[0] == prey and edge[1] not in self.sinks:
            predators.append(edge[1])
        if len(predators) == 0:
          continue
        pred_rates = {predator:0 for predator in predators}
        desired_edges = {predator:self.edges[(prey,predator)] for predator in predators}
        new_edges = self.get_new_edge_weights(prey,predators,self.get_output(prey),pred_rates)
        while True:
          changed = False
          for predator in predators:
            new_edges = self.get_new_edge_weights(prey,predators,self.get_output(prey),pred_rates)
            #print pred_rates,new_edges,desired_edges
            if new_edges[predator] < desired_edges[predator] - 0.1:
              changed = True
              pred_rates[predator] += 0.00001*(desired_edges[predator] - new_edges[predator])
            elif new_edges[predator] > desired_edges[predator] + 0.1:
              changed = True
              pred_rates[predator] += 0.00001*(desired_edges[predator] - new_edges[predator])
          if not changed:
            break
        for predator in pred_rates:
          self.eat_rates[(prey,predator)] = pred_rates[predator]

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

  def iterative(self,event_node,new_mass):
    self.biomass[event_node] = new_mass
    for prey in self.get_prey(event_node):
      self.update_edges_from_weights(prey,self.get_new_edge_weights(prey,self.get_predators(prey),self.get_postsink_output(prey)))
      self.update_biomass(prey)
    print self.biomass, self.edges
    while True:
      permut = list(self.nodelist)
      random.shuffle(permut)
      prev_biomass = dict(self.biomass)
      prev_edges = dict(self.edges)
      for prey in permut:
        if prey in self.sinks:
          continue
        self.update_edges_from_weights(prey,self.get_new_edge_weights(prey,self.get_predators(prey),self.get_postsink_output(prey)))
        self.update_biomass(prey)
        print prey, self.biomass, self.edges
      max_diff = 0
      for node in self.nodelist:
        max_diff = max([abs(self.biomass[node]-prev_biomass[node]),max_diff])
      for edge in self.edges:
        max_diff = max([abs(self.edges[edge]-prev_edges[edge]),max_diff])
      if max_diff < 1:
        break
    print self.biomass,self.edges

  def update_edges_from_weights(self,prey,pred_weights):
    for predator in pred_weights:
      self.edges[(prey,predator)] = pred_weights[predator]

  def get_predators(self,node):
    return [predator for (prey,predator) in self.edges if prey == node and predator not in self.sinks]

  def get_prey(self,node):
    return [prey for (prey,predator) in self.edges if predator == node]

  def get_input(self,node):
    return sum([self.edges[edge] for edge in self.edges if edge[1] == node])

  def get_postsink_output(self,node):
    return self.biomass[node]*self.output_props[node]# * (1-self.sink_props[node])

  def get_output(self,node):
    return sum([self.edges[edge] for edge in self.edges if edge[0] == node])

  def get_inout_diff(self,node,edges):
    return sum([edges[edge] for edge in edges if edge[1] == node]) - sum([edges[edge] for edge in edges if edge[0] == node])

  # def get_isolated_edge_weight(self,prey,predator,prey_biomass):
  #   if prey in self.sources:
  #     return min(self.biomass[prey]+self.edges[(prey,predator)],self.biomass[predator] * self.eat_rates[(prey,predator)])
  #   temp_prey = prey_biomass
  #   new_edge = 0
  #   for i in range(int(self.biomass[predator])):
  #     new_edge += temp_prey * self.eat_rates[(prey,predator)]
  #     temp_prey -= temp_prey * self.eat_rates[(prey,predator)]
  #   return max(0,new_edge)

  def get_new_edge_weights(self,prey,predators,prey_biomass,rates=None):
    if len(predators) == 0:
      return {}
    if rates is None:
      rates = {predator:self.eat_rates[(prey,predator)] for predator in predators if predator not in self.sinks}
    if prey in self.sources:
      desires = {predator:self.biomass[predator]*self.eat_rates[(prey,predator)] for predator in predators}
      #print desires
      if sum(desires.values()) <= self.sources[prey]:
        return desires
      else:
        desires_nor = {predator:desires[predator]*1.0/sum(desires.values())*self.sources[prey] for predator in desires}
        return desires_nor
    temp_prey = prey_biomass
    new_edges = {predator:0 for predator in predators}
    predator_masses = {predator:1.0*self.biomass[predator] for predator in predators}
    predator_masses = {predator:mass for predator,mass in predator_masses.iteritems() if mass > 0}
    if len(predator_masses) == 0 or prey_biomass == 0 or self.biomass[prey] == 0:
      return new_edges
    p_masses_nor = {predator:mass/min(predator_masses.values()) for predator,mass in predator_masses.iteritems()}
    for i in range(int(min(predator_masses.values()))):
      p_items = p_masses_nor.items()
      random.shuffle(p_items)
      for predator,mass in p_items:
        new_edges[predator] += temp_prey * mass * rates[predator]
        temp_prey -= temp_prey * mass * rates[predator]
    return new_edges

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

edges = {(0,1):1000,(1,2):200,(1,4):100,(2,3):50,(2,5):50,(5,6):25,(3,6):25,(4,6):25,(2,6):50}
sources = {0:2000}
sinks = [6]
algo = CascadeAlgorithm(edges,sources,sinks,5)
algo.iterative(2,100)
