from pajek_reader import read_pajek_file
from cascade import TurnAlgorithm
import snap
import math

import pprint
pp = pprint.PrettyPrinter(indent=2)

# if __name__ == "__main__":

input_file = 'Webs_paj/Florida.paj'
nodeInfo, edgeWeights = read_pajek_file(input_file)

G = snap.TNGraph.New() # directed graph
for nodeId in nodeInfo:
  G.AddNode(nodeId)
for edge in edgeWeights:
  G.AddEdge(edge[0], edge[1])

def initialize_turn_algorithm(node_info, edge_weights, min_biomass):
  masses = {}
  sources = []
  sinks = []
  piles = []
  for node_id in node_info:
    masses[node_id] = node_info[node_id]['biomass']
    if node_info[node_id]['type'] == 2:
      piles.append(node_id)
    elif node_info[node_id]['type'] == 3:
      sources.append(node_id)
    elif node_info[node_id]['type'] in [4,5]:
      sinks.append(node_id)
  algo = TurnAlgorithm(masses, edge_weights, sources, sinks, piles, min_biomass)
  return algo

def get_change_impact(algo, event_node, new_mass):
  algo.reset()
  mass_flow, average_masses = algo.turns(event_node, new_mass, iters=10000, verbose=True)
  final_masses = {node:average_masses[node] if algo.biomass[node] > 0 else 0 for node in algo.nodelist if algo.default_biomass[node] > 0}
  extinctions = 0
  relative_sizes = {}
  for node_id in final_masses:
    if node_id == event_node:
      continue
    if final_masses[node_id] == 0:
      extinctions += 1
    relative_sizes[node_id] = final_masses[node_id]/algo.default_biomass[node_id]
  impact_score = sum([math.pow(relative_sizes[node_id]-1,2) for node_id in relative_sizes]) + 0.5 * extinctions
  return impact_score


# snap.PrintInfo(G, "Python type PNGraph", "test.txt", False)

# adds 'trophic_level' key to each nodeInfo
# -1: input
# 0 : detritivores
# 1 : autotrophs
# 2 : primary consumers (herbivores)
# 3 : secondary consumers (omnivores)
# 4 : predators (carnivores)
def analyzeTrophicLevels(G, nodeInfo, edgeWeights):
  # get nodeId of input (Sun)
  inputId = [nodeId for nodeId, info in nodeInfo.items() if info['type'] == 3]
  inputId = inputId[0]
  nodeInfo[inputId]['trophic_level'] = -1

  # mark all detritivores
  # - take input from detritus
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      continue
    node = G.GetNI(nodeId)
    for preyId in node.GetInEdges():
      if nodeInfo[preyId]['type'] == 2:
        nodeInfo[nodeId]['trophic_level'] = 0
        break

  # mark all autotrophs (can overwrite detritivores)
  # - take input from Sun
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      continue
    if (inputId, nodeId) in edgeWeights:
      nodeInfo[nodeId]['trophic_level'] = 1

  # mark all primary consumers (can overwrite autotrophs)
  # - eat autotrophs or detritovores
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      continue
    node = G.GetNI(nodeId)
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel in [0, 1]:
          nodeInfo[nodeId]['trophic_level'] = 2
          break

  # mark all herbivores (can overwrite primary consumers)
  # - all herbivores are primary consumers who also eat other primary consumers
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      continue
    if 'trophic_level' not in nodeInfo[nodeId] or nodeInfo[nodeId]['trophic_level'] != 2: # ignore non-primary consumers
      continue
    node = G.GetNI(nodeId)
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel == 2:
          nodeInfo[nodeId]['trophic_level'] = 3
          break

  # mark all carnivores
  # - eat only primary consumers and herbivores
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      continue
    if 'trophic_level' in nodeInfo[nodeId]: # ignore organisms that have already been asigned a trophic level
      continue
    isCarnivore = True
    node = G.GetNI(nodeId)
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel < 2:
          isCarnivore = False
          break
    if isCarnivore:
      nodeInfo[nodeId]['trophic_level'] = 4

analyzeTrophicLevels(G, nodeInfo, edgeWeights)

# pp.pprint(nodeInfo)

#pp.pprint(nodeInfo)
#pp.pprint(calculatePercentBiomass(nodeInfo))