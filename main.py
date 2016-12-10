from pajek_reader import read_pajek_file
from cascade import TurnAlgorithm
import snap
import math
import matplotlib.pyplot as plt

import pprint
pp = pprint.PrettyPrinter(indent=2)

### Parameters ###
input_file_paths = ['Webs_paj/Chesapeake.paj', 'Webs_paj/Florida.paj']
min_biomass = 0.1
destruction_type = 'random'
destruction_mass = 10

def main():
  # results = {
  #   file_path =>
  #     {
  #       node_ids: [],
  #       degree_centr: [],
  #       etc..
  #     }
  # }
  results = {}

  for input_file_path in input_file_paths:
    G, node_info, edge_weights = setup_graph(input_file_path)
    results[input_file_path] = calculate_centrality(G, node_info)

    print '\tRunning model'
    algo = initialize_turn_algorithm(node_info, edge_weights, min_biomass)
    impact_scores = []
    for node_id in results[input_file_path]['node_ids']:
      node = node_info[node_id]
      impact_scores.append(get_change_impact(algo, node_id, destruction_mass))
      # if node_id % 1 == 0:
      print '\t\tFinished running model for node %d' % node_id
    results[input_file_path]['impact_scores'] = impact_scores

  create_plots(results)

def calculate_centrality(G, node_info):
  print '\tCalculating centrality measures for every node in graph'
  data = {
    'node_ids': [],
    'degree': [],
    'close_centr': [],
    'between_centr': [],
    'page_rank': []
  }

  # (exact) betweenness centrality for every node and edge
  node_between_cent = snap.TIntFltH() # {node_id => betweenness centrality}
  edge_between_cent = snap.TIntPrFltH() # {(n1,n2) => betweenness centrality}
  snap.GetBetweennessCentr(G, node_between_cent, edge_between_cent, 1.0)

  # PageRank score of every node
  page_rank = snap.TIntFltH() # {node_id => PageRank score}
  snap.GetPageRank(G, page_rank)

  for node_id, node in node_info.iteritems():
    data['node_ids'].append(node_id)
    data['degree'].append(G.GetNI(node_id).GetDeg())
    data['close_centr'].append(snap.GetClosenessCentr(G, node_id))
    data['between_centr'].append(node_between_cent[node_id])
    data['page_rank'].append(page_rank[node_id])

  return data

def setup_graph(input_file_path):
  print 'Reading in nodes and edges from %s' % (input_file_path, )
  node_info, edge_weights = read_pajek_file(input_file_path)
  G = snap.TNGraph.New() # directed graph
  for nodeId in node_info:
    G.AddNode(nodeId)
  for edge in edge_weights:
    G.AddEdge(edge[0], edge[1])
  return G, node_info, edge_weights

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

def get_change_impact(algo, event_node, new_mass, num_iters=3, verbose=False):
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
    relative_sizes[node_id] = final_masses[node_id]/float(algo.default_biomass[node_id])
  impact_score = sum([math.pow(relative_sizes[node_id]-1,2) for node_id in relative_sizes]) + 0.5 * extinctions
  # if impact_score > 10:
  #   pp.pprint(relative_sizes)
  return impact_score / len(final_masses)

def create_plots(results):
  indep_vars = ['degree', 'close_centr', 'between_centr', 'page_rank']
  y = 'impact_scores'

  for input_file_path in input_file_paths:
    data = results[input_file_path]
    for x in indep_vars:
      plt.figure(x)
      plt.plot(data[x], data[y], 'o')
  
  for x in indep_vars:
    plt.figure(x)
    plt.grid(True)
    plt.xlabel(x)
    plt.ylabel('Impact Score')
    plt.legend(input_file_paths)

    plt.savefig('graphs\\%s.png' % x, format="png", transparent=True)
    plt.cla()

if __name__ == "__main__":
  main()