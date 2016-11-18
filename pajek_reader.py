def read_pajek_file(input_file):
  all_lines = []
  with open(input_file, 'r') as f:
    # skip all blank lines and comment lines
    for line in f:
      stripped_line = line.strip()
      if stripped_line and stripped_line[0] != '%':
        all_lines.append(stripped_line)

  # nodeId (int) : {
  #   'type': int, # 1-5
  #   'biomass': float,
  #   'name': str
  # }
  nodeInfo = {}

  # directed edge weights (biomass flow)
  #   (nodeId1, nodeId2) => float
  edgeWeights = {}

  i = 0
  while i < len(all_lines):
    line = all_lines[i].split()
    if line[0][0] == '*':
      special_token = line[0][1:]
      if special_token == 'partition':
        i = processTypes(all_lines, i, nodeInfo)
      elif special_token == 'network':
        i = processNetwork(all_lines, i, nodeInfo, edgeWeights)
      elif special_token == 'vector':
        i = processBiomass(all_lines, i, nodeInfo)
      else:
        raise 'Invalid special token', special_token
    else:
      raise 'Expecting line starting with *', line[0][0]

  return nodeInfo, edgeWeights

# Node Types
# 1 - Living/producing compartment
# 2 - Other compartment
# 3 - Input
# 4 - Output
# 5 - Respiration
def processTypes(all_lines, curr, nodeInfo):
  initial_line = all_lines[curr].split()
  assert initial_line[0] == '*partition'
  curr+=1

  numNodes = int(all_lines[curr].split()[1])
  curr+=1

  for nodeId in xrange(1, numNodes+1):
    nodeType = int(all_lines[curr])
    assert (nodeType in range(1,6)), 'node type must be from 1 to 5'

    if nodeId not in nodeInfo:
      nodeInfo[nodeId] = {}
    nodeInfo[nodeId]['type'] = nodeType
    curr+=1
  return curr

def processNetwork(all_lines, curr, nodeInfo, edgeWeights):
  initial_line = all_lines[curr].split()
  assert initial_line[0] == '*network'
  curr+=1

  numNodes = int(all_lines[curr].split()[1])
  assert (numNodes == len(nodeInfo)), 'Mismatch in number of nodes'
  curr+=1

  for curr in xrange(curr, curr+numNodes):
    nodeLine = all_lines[curr].split()
    nodeId = int(nodeLine[0])
    nodeName = nodeLine[1]

    nodeInfo[nodeId]['name'] = nodeName
  curr+=1

  assert (all_lines[curr] == '*arcs'), 'Expected *arcs'
  curr+=1

  while True:
    edgeLine = all_lines[curr].split()
    if edgeLine[0][0] == '*':
      break

    n1 = int(edgeLine[0])
    n2 = int(edgeLine[1])
    weight = float(edgeLine[2])

    edgeWeights[(n1,n2)] = weight
    curr+=1

  return curr

def processBiomass(all_lines, curr, nodeInfo):
  initial_line = all_lines[curr].split()
  assert initial_line[0] == '*vector'
  curr+=1

  numNodes = int(all_lines[curr].split()[1])
  assert (numNodes == len(nodeInfo)), 'Mismatch in number of nodes'
  curr+=1

  for nodeId in xrange(1, numNodes+1):
    biomass = float(all_lines[curr])
    nodeInfo[nodeId]['biomass'] = biomass
    curr+=1
  return curr