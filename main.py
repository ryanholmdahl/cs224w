from pajek_reader import read_pajek_file
from cascade import TurnAlgorithm
import snap
import math
import matplotlib.pyplot as plt
import cPickle
import numpy as np

import pprint
pp = pprint.PrettyPrinter(indent=2)

### Parameters ###
input_file_paths = ["Webs_paj/Narragan.paj","Webs_paj/StMarks.paj",'Webs_paj/Chesapeake.paj',"Webs_paj/Mondego.paj",'Webs_paj/Michigan.paj']
min_biomass = 0
destruction_type = 'random'
destruction_mass = 0

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
    results[input_file_path] = calculate_centrality(G, node_info, edge_weights)
    print '\tRunning model'
    algo = initialize_turn_algorithm(node_info, edge_weights, min_biomass)
    impact_scores = []
    for node_id in results[input_file_path]['node_ids']:
      node = node_info[node_id]
      impact_scores.append(get_change_impact(algo, node_id, destruction_mass))
      # if node_id % 1 == 0:
      print '\t\tFinished running model for node %d' % node_id
    results[input_file_path]['impact_scores'] = impact_scores
    cPickle.dump(results[input_file_path],open("pkls/"+input_file_path.split('/')[1]+".pkl","wb"))
  create_plots(results)

def calculate_centrality(G, node_info, edge_weights):
  print '\tCalculating centrality measures for every node in graph'
  data = {
    'node_ids': [],
    'degree': [],
    'in_degree': [],
    'out_degree': [],
    'close_centr': [],
    'close_centr_undir': [],
    'between_centr': [],
    'between_centr_undir': [],
    'page_rank': [],
    'multi_page_rank': [],
    'multi_page_rank_rev': [],
    'throughflow': [],
    'biomass': []
  }

  # (exact) betweenness centrality for every node and edge
  node_between_cent_undir = snap.TIntFltH() # {node_id => betweenness centrality}
  edge_between_cent_undir = snap.TIntPrFltH() # {(n1,n2) => betweenness centrality}
  snap.GetBetweennessCentr(G, node_between_cent_undir, edge_between_cent_undir, 1.0)

  node_between_cent = snap.TIntFltH() # {node_id => betweenness centrality}
  edge_between_cent = snap.TIntPrFltH() # {(n1,n2) => betweenness centrality}
  snap.GetBetweennessCentr(G, node_between_cent, edge_between_cent, 1.0, True)

  # PageRank score of every node
  page_rank = snap.TIntFltH() # {node_id => PageRank score}
  snap.GetPageRank(G, page_rank)

  #Multigraph PageRank score of every node
  total_input = sum(edge_weights[edge] for edge in edge_weights if node_info[edge[0]]["type"]==3)
  multigraph = snap.GenRndGnm(snap.PNEANet, 100, 1000)
  multigraph.Clr()
  for nodeId in node_info:
    multigraph.AddNode(nodeId)
  for edge in edge_weights:
    for _ in range(int(edge_weights[edge]*10000.0/total_input)+1):
      multigraph.AddEdge(edge[0], edge[1])
  multi_page_rank = snap.TIntFltH() # {node_id => PageRank score}
  snap.GetPageRank(multigraph, multi_page_rank)

  multigraph_rev = snap.GenRndGnm(snap.PNEANet, 100, 1000)
  multigraph_rev.Clr()
  for nodeId in node_info:
    multigraph_rev.AddNode(nodeId)
  for edge in edge_weights:
    for _ in range(int(edge_weights[edge]*10000.0/total_input)+1):
      multigraph_rev.AddEdge(edge[1], edge[0])
  multi_page_rank_rev = snap.TIntFltH() # {node_id => PageRank score}
  snap.GetPageRank(multigraph_rev, multi_page_rank_rev)

  for node_id, node in node_info.iteritems():
    data['node_ids'].append(node_id)
    data['degree'].append(G.GetNI(node_id).GetDeg())
    data['in_degree'].append(G.GetNI(node_id).GetInDeg())
    data['out_degree'].append(G.GetNI(node_id).GetOutDeg())
    data['close_centr'].append(snap.GetClosenessCentr(G, node_id,True,True))
    data['close_centr_undir'].append(snap.GetClosenessCentr(G, node_id))
    data['between_centr'].append(node_between_cent[node_id])
    data['between_centr_undir'].append(node_between_cent_undir[node_id])
    data['page_rank'].append(page_rank[node_id])
    data['multi_page_rank'].append(multi_page_rank[node_id])
    data['multi_page_rank_rev'].append(multi_page_rank_rev[node_id])
    data['throughflow'].append(sum(edge_weights[edge] for edge in edge_weights if edge[1] == node_id))
    data['biomass'].append(node_info[node_id]["biomass"])

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

def get_change_impact(algo, event_node, new_mass, num_iters=100000, verbose=False):
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
  impact_score = sum([math.pow(min(relative_sizes[node_id]-1,0),2) for node_id in relative_sizes])
  print impact_score/len(final_masses)
  # if impact_score > 10:
  #   pp.pprint(relative_sizes)
  return impact_score / len(final_masses)


def get_correlations(results):
  indep_vars = ['degree', 'close_centr', 'between_centr', 'page_rank', 'multi_page_rank', 'multi_page_rank_rev', 'throughflow', 'biomass', 'in_degree', 'out_degree', 'close_centr_undir', 'between_centr_undir']
  y = 'impact_scores'
  corrcoefs = {var:[] for var in indep_vars}
  for input_file_path in input_file_paths:
    data = results[input_file_path]
    for x in indep_vars:
      xobs = np.array(data[x])
      yobs = np.array(data[y])
      corrcoefs[x].append(np.corrcoef(xobs,yobs)[1,0])
  corr_measures = {x:{"mean":sum(corrcoefs[x])/len(corrcoefs[x])} for x in corrcoefs}
  for x in corr_measures:
    corr_measures[x]["variance"] = sum((val-corr_measures[x]["mean"])**2 for val in corrcoefs[x])/(len(corrcoefs[x])-1)
  return corr_measures


def create_plots(results,logx=False):
  indep_vars = ['degree', 'close_centr', 'between_centr', 'page_rank', 'multi_page_rank', 'multi_page_rank_rev', 'throughflow', 'biomass', 'in_degree', 'out_degree', 'close_centr_undir', 'between_centr_undir']
  y = 'impact_scores'

  for input_file_path in input_file_paths:
    data = results[input_file_path]
    for x in indep_vars:
      plt.figure(x)
      if logx:
        plt.semilogx(data[x], data[y], 'o')
      else:
        plt.plot(data[x], data[y], 'o')

  corr_measures = {x:{"mean":sum(corrcoefs[x])/len(corrcoefs[x])} for x in corrcoefs}
  for x in corr_measures:
    corr_measures[x]["variance"] = sum((val-corr_measures[x]["mean"])**2 for val in corrcoefs[x])/(len(corrcoefs[x])-1)
  print corr_measures

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
