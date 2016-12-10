from main import initialize_turn_algorithm, get_change_impact
from cascade import TurnAlgorithm

masses = {0: 0, 1: 0, 2: 300, 3: 1000, 4: 200, 5: 200, 6: 100}
edges = {(0, 3): 1000, (3, 4): 600, (3, 1): 200, (3, 2): 200, (4, 6): 300, (4, 1): 150, (4, 2): 150,
             (2, 5): 350,
             (5, 6): 100, (5,1): 250, (6, 1): 400}
sources = [0]
sinks = [1]
piles = [2]
algo = TurnAlgorithm(masses, edges, sources, sinks, piles, 0.1)
print get_change_impact(algo, 3, 000)