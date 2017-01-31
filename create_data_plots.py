from pajek_reader import read_pajek_file
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