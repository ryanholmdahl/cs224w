import cPickle
from main import get_correlations, setup_graph, plot_correlations, create_plots

results = {}
ignore_nodes = {}
for filename in ["pkls/ChesLower.paj.pkl", "pkls/ChesMiddle.paj.pkl", "pkls/ChesUpper.paj.pkl", "pkls/CrystalC.paj.pkl",
                 "pkls/CrystalD.paj.pkl", "pkls/Chesapeake.paj.pkl", "pkls/Michigan.paj.pkl", "pkls/Mondego.paj.pkl",
                 "pkls/Narragan.paj.pkl", "pkls/StMarks.paj.pkl"]:
  data = cPickle.load(open(filename, "rb"))
  results["Webs_paj/" + filename.split("/")[1].replace(".pkl", "")] = data
  G, node_info, edge_weights = setup_graph("Webs_paj/" + filename.split("/")[1].replace(".pkl", ""))
  ignore_nodes["Webs_paj/" + filename.split("/")[1].replace(".pkl", "")] = [node_id for node_id in node_info if
                                                                            node_info[node_id]["type"] != 1]
corrcoefs, measures = get_correlations(results, ignore_nodes)
measure_names = {'multi_page_rank_rev': "Reversed Weighted PageRank", 'multi_page_rank': "Weighted PageRank",
                'page_rank': "PageRank", "between_centr": "Betweenness", "close_centr": "Closeness",
                "throughflow": "Throughflow", "out_degree": "Out Degree", "biomass": "Biomass",
                "in_degree": "In Degree", "degree": "Degree"}
create_plots(results,ignore_nodes=ignore_nodes)