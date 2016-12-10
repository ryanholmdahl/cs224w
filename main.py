from pajek_reader import read_pajek_file
from cascade import TurnAlgorithm
import snap
import math

import pprint
pp = pprint.PrettyPrinter(indent=2)

### Parameters ###
input_file_path = 'Webs_paj/Florida.paj'
min_biomass = 0.1
destruction_type = 'random'
destruction_mass = 10

### Global Vars ###
node_info = None
edge_weights = None

def main():
  G = setup_graph(input_file_path)
  algo = initialize_turn_algorithm(node_info, edge_weights, min_biomass)

  victim_node, destruction_score = wreck_havoc(algo, G, destruction_type)
  analyze_graph(G)

def wreck_havoc(algo, G, destruction_type):
  victim_node = 0
  if destruction_type == 'random':
    victim_node = random.choose(node_info.keys())
  elif destruction_type == 'highest_degree':
    victim_node = snap.GetMxDegNId(G)
  elif destruction_type == 'largest_biomass':
    max_mass = 0
    for node_id, node in node_info.iteritems():
      if node['biomass'] > max_mass:
        victim_node = node_id
  
  print 'Chose node %d (%s) as victim for destruction' % (victim_node, node_info[victim_node]['name'])
  print 'Wrecking havoc...'
  return victim_node, get_change_impact(algo, victim_node, destruction_mass)

def analyze_graph(G):
  # in-degree distribution
  in_degree_distr = snap.TIntPrV() # [(degree, count)]
  snap.GetInDegCnt(G, in_degree_distr)
  
  # out-degree distribution
  out_degree_distr = snap.TIntPrV() # [(degree, count)]
  snap.GetOutDegCnt(Graph, out_degree_distr)

  # (exact) betweenness centrality for every node and edge
  node_between_cent = snap.TIntFltH() # {node_id => betweenness centrality}
  edge_between_cent = snap.TIntPrFltH() # {(n1,n2) => betweenness centrality}
  snap.GetBetweennessCentr(G, node_between_cent, edge_between_cent, 1.0)

  # PageRank score of every node
  page_rank = snap.TIntFltH() # {node_id => PageRank score}
  snap.GetPageRank(G, page_rank)

  return in_degree_distr, out_degree_distr, node_between_cent, edge_between_cent, page_rank

def setup_graph(input_file_path):
  global node_info, edge_weights
  print 'Reading in nodes and edges from %s' % (input_file_path, )
  node_info, edge_weights = read_pajek_file(input_file_path)
  G = snap.TNGraph.New() # directed graph
  for nodeId in node_info:
    G.AddNode(nodeId)
  for edge in edge_weights:
    G.AddEdge(edge[0], edge[1])
  return G

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

def get_change_impact(algo, event_node, new_mass, num_iters=10000, verbose=False):
  algo.reset()
  mass_flow, average_masses = algo.turns(event_node, new_mass, iters=num_iters, verbose=verbose)
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

if __name__ == "__main__":
  main()