from pajek_reader import read_pajek_file
from main import analyzeTrophicLevels
import snap
from matplotlib import pyplot as plt
from collections import Counter

input_file = 'Webs_paj/Florida.paj'
nodeInfo, edgeWeights = read_pajek_file(input_file)

G = snap.TNGraph.New() # directed graph
for nodeId in nodeInfo:
  G.AddNode(nodeId)
for edge in edgeWeights:
  G.AddEdge(edge[0], edge[1])

analyzeTrophicLevels(G,nodeInfo,edgeWeights)

def calculatePercentBiomass(nodeInfo):
  biomass = [0] * 6
  for nodeId, info in nodeInfo.items():
    if info['type'] == 1: # living organism
      trophic_level = info['trophic_level']
      biomass[trophic_level] += info['biomass']
    elif info['type'] == 2: # detritus
      biomass[5] += info['biomass']

  # normalize
  total = float(sum(biomass))
  biomass = [x/total for x in biomass]

  return biomass

def getTrophicSpeciesDistribution(nodeInfo):
  trophic_counts = [0 for i in range(5)]
  for node,info in nodeInfo.iteritems():
    if "trophic_level" in info and info["trophic_level"] >= 0:
      trophic_counts[info["trophic_level"]] += 1
  return [trophic_counts[i]*1.0/sum(trophic_counts) for i in range(len(trophic_counts))]

def getTrophicDegreeDistribution(G,nodeInfo):
  in_degrees_by_level = [[] for i in range(5)]
  out_degrees_by_level = [[] for i in range(5)]
  for node,info in nodeInfo.iteritems():
    if "trophic_level" not in info or info["trophic_level"] < 0:
      continue
    ni = G.GetNI(node)
    in_deg = ni.GetInDeg()
    out_deg = ni.GetOutDeg()
    in_degrees_by_level[info["trophic_level"]].append(in_deg)
    out_degrees_by_level[info["trophic_level"]].append(out_deg)
  in_degree_counters = [dict(Counter(in_list)) for in_list in in_degrees_by_level]
  out_degree_counters = [dict(Counter(out_list)) for out_list in out_degrees_by_level]
  return [{degree:count*1.0/sum(counter.values()) for degree,count in counter.iteritems()} for counter in in_degree_counters],\
         [{degree:count*1.0/sum(counter.values()) for degree,count in counter.iteritems()} for counter in out_degree_counters]


analyzeTrophicLevels(G, nodeInfo, edgeWeights)
species_dist = getTrophicSpeciesDistribution(nodeInfo)
labels = ("Detritovore","Autotroph","Primary","Omnivore","Carnivore")
colors = ('r','b','g','y','c')
y_pos = range(len(labels))
plt.bar(y_pos,species_dist,align='center',alpha=0.5)
plt.xticks(y_pos,labels)
plt.ylabel("Proportion")
plt.title("Florida Species Distribution by Trophic Level")
plt.savefig("species-dist-florida.png")

in_degs,out_degs = getTrophicDegreeDistribution(G,nodeInfo)
plt.clf()
all_ticks = []
for i in range(len(in_degs)):
  for key in in_degs[i]:
    if key not in all_ticks:
      all_ticks.append(key)
all_ticks.sort()
for i in range(len(in_degs)):
  plt.bar([key+i*1.0/(len(labels)+1) for key in all_ticks],[in_degs[i][key] if key in in_degs[i] else 0 for key in all_ticks],1.0/(len(labels)+1),label=labels[i],color=colors[i])
plt.legend()
plt.ylabel("Proportion")
plt.xlabel("In-Degree")
plt.xticks([key+len(in_degs)*0.5/(len(labels)+1) for key in all_ticks],range(max(all_ticks)+1))
plt.yticks([0.2 * i for i in range(6)])
plt.title("Florida In-Degrees by Trophic Level")
plt.savefig("indeg-florida.png")

plt.clf()
all_ticks = []
for i in range(len(out_degs)):
  for key in out_degs[i]:
    if key not in all_ticks:
      all_ticks.append(key)
all_ticks.sort()
for i in range(len(out_degs)):
  plt.bar([key+i*1.0/(len(labels)+1) for key in all_ticks],[out_degs[i][key] if key in out_degs[i] else 0 for key in all_ticks],1.0/(len(labels)+1),label=labels[i],color=colors[i])
plt.legend()
plt.ylabel("Proportion")
plt.xlabel("Out-Degree")
plt.xticks([key+len(out_degs)*0.5/(len(labels)+1) for key in range(max(all_ticks)+1)],range(max(all_ticks)+1))
plt.yticks([0.2 * i for i in range(6)])
plt.title("Florida Out-Degrees by Trophic Level")
plt.savefig("outdeg-florida.png")