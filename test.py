masses = {0:0, 1:0, 2:200, 3:100, 4:100}
edges = {(0,3):100, (3,1):50, (3,2):50, (2,4):100, (4,1):50, (4,2):50}
sources = [0]
sinks = [1]
piles = [2]
algo = TurnAlgorithm(masses, edges, sources, sinks, piles, 10, 1e-6, 1e-3)
algo.turn_eat_rates(verbose=False)
print algo.eat_rates
print ""
mass_flow, average_masses = algo.turns(2, 10, iters=10000, verbose=False)
print average_masses
print algo.biomass