import networkx as nx
from pajek_reader import read_pajek_file
from matplotlib import pyplot as plt


def output_graph_file(node_info, edge_weights, name):
    id_to_name = {}
    id_to_mass = {}
    id_to_type = {}
    for node_id in node_info:
        id_to_name[node_id] = node_info[node_id]['name']
        id_to_mass[node_id] = node_info[node_id]['biomass']
        id_to_type[node_id] = node_info[node_id]['type']
    g = nx.DiGraph()
    for node_id in id_to_name:
        g.add_node(node_id,
                   attr_dict={"name": id_to_name[node_id], "biomass": id_to_mass[node_id], "type": id_to_type[node_id]})
    for edge in edge_weights:
        g.add_edge(edge[0], edge[1], attr_dict={"weight": edge_weights[edge]})
    nx.write_graphml(g, name + ".graphml")


# nodeInfo, edgeWeights = read_pajek_file('Webs_paj/Chesapeake.paj')
nodeInfo = {0: {"name": "input", "biomass": 0, "type": 3}, 1: {"name": "respiration", "biomass": 0, "type": 5},
            2: {"name": "detritus", "biomass": 300, "type": 2}, 3: {"name": "plant", "biomass": 1000, "type": 1},
            4: {"name": "primary", "biomass": 200, "type": 1}, 5: {"name": "detritovore", "biomass": 200, "type": 1},
            6: {"name": "secondary", "biomass": 100, "type": 1}}
edgeWeights = {(0, 3): 1000, (3, 4): 600, (3, 1): 200, (3, 2): 200, (4, 6): 300, (4, 1): 150, (4, 2): 150,
               (2, 5): 350,
               (5, 6): 100, (5, 1): 250, (6, 1): 200, (6, 2): 200}
output_graph_file(nodeInfo, edgeWeights, "test")
