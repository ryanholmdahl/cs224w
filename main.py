from pajek_reader import read_pajek_file
import snap

# if __name__ == "__main__":

input_file = 'Webs_paj/Chesapeake.paj'
nodeInfo, edgeWeights = read_pajek_file(input_file)

G = snap.TNGraph.New() # directed graph
for nodeId in nodeInfo:
  G.AddNode(nodeId)
for edge in edgeWeights:
  G.AddEdge(edge[0], edge[1])

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
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      pass
    for preyId in node.GetInEdges():
      if nodeInfo[preyId]['type'] == 2:
        nodeInfo[nodeId]['trophic_level'] = 0
        break

  # mark all autotrophs (can overwrite detritivores)
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      pass
    if (inputId, nodeId) in edgeWeights:
      nodeInfo[nodeId]['trophic_level'] = 1

  # mark all primary consumers (can overwrite autotrophs)
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      pass
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel == 1:
          nodeInfo[nodeId]['trophic_level'] = 2
          break

  # mark all herbivores (can overwrite primary consumers)
  # - all herbivores are primary consumers who also eat other primary consumers
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      pass
    if nodeInfo[nodeId]['trophic_level'] != 2: # ignore non-primary consumers
      pass
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel == 2:
          nodeInfo[nodeId]['trophic_level'] = 3
          break

  # mark all carnivores
  for nodeId in nodeInfo:
    if nodeInfo[nodeId]['type'] != 1: # ignore non-living organisms
      pass
    isCarnivore = True
    for preyId in node.GetInEdges():
      if 'trophic_level' in nodeInfo[preyId]:
        preyLevel = nodeInfo[preyId]['trophic_level']
        if preyLevel < 2:
          isCarnivore = False
          break
    if isCarnivore:
      nodeInfo[nodeId]['trophic_level'] = 4

analyzeTrophicLevels(G, nodeInfo, edgeWeights)