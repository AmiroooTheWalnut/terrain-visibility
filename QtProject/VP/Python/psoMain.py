import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF
from mlCommon import GuardEnv
from common import fibonacci_lattice, square_uniform, setupGraph
import pyswarms as ps
import time
import copy
import sys

lastComps = []
lastGuards = []

#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
def bsfScore(guard_positions):
    global lastComps, lastGuards

    # Don't move the guards that were seeing North or South
    # We don't know if the guard will still see N/S even if the guard moves E/W, 
    # So we need to keep the guard at its last position (both x and y)
    if keepNS:
        for comp in lastComps:
            if comp.minX == 0 or comp.maxX == nrows-1:
                id = comp.parentID
                guard_positions[id] = (lastGuards[id].x, lastGuards[id].y)

    # Don't move the guards that had at least N (threshold) intersecting components
    if threshold != None:
        for comp in lastComps:
            if len(comp.intersects) >= threshold:
                id = comp.parentID
                guard_positions[id] = (lastGuards[id].x, lastGuards[id].y)

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, bitmap, verbose)
    if ilp:
        cost = runILP(bitmap, gGuards, gComps, gNorths, gSouths, verbose, enableShow)
    else:
        cost = runBSF(bitmap, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    print(f"Cost = {cost}", flush=True)

    #print(guard_positions, flush=True)

    lastComps.clear()
    lastComps = gComps.copy()
    lastGuards.clear()
    lastGuards = gGuards.copy()

    return cost  # Lower cost the better

if __name__ == "__main__":
    sys.stdout = open('psoMainLog.txt', 'a')
    print("=============psoMain.py Run Start===============", flush=True)

    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--height', type=int, help="10")
    parser.add_argument('--ilp', action='store_true', help="Run ILP")
    parser.add_argument('--square', action='store_true', help="Square uniform")
    parser.add_argument('--randomize', action='store_true', help="Randomize Square Pos")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")
    parser.add_argument('--keepNS', action='store_true', help="Keep NS guard pos")
    parser.add_argument('--threshold', type=int, help="Connectivity threshold to keep guard pos")

    args = parser.parse_args()

    filename = args.name        # None if not provided
    radius = args.radius        # None if not provided
    numGuards = args.numGuards  # None if not provided
    guardHt = args.height       # Default if not provided
    ilp = args.ilp              # False if not provided
    squareUniform = args.square # False if not provided
    randomize = args.randomize  # False if not provided (Only applicable if squareUniform is true)
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided
    keepNS = args.keepNS        # None if not provided
    threshold = args.threshold   # None if not provided

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    nrows, ncols = bitmap.shape

    # Initial guard positions determined by fibonacci lattice
    if squareUniform:
        guard_positions = square_uniform(numGuards, nrows, ncols, randomize)
        numGuards = guard_positions.shape[0] # numGuards must be perfect square
    else:
        guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    # Get a baseline
    cost = bsfScore(guard_positions)

    # Define bounds for the guards to not exceed the bitmap
    num_dimensions = 2
    lb = np.array([0, 0])
    ub = np.array([nrows-1, ncols-1])
   
    # Two approaches:
    # Option 1: n_particles = numGuards, num_dimensions = 2     - Optimize individual position    
    # Option 2: n_particles = 1, num_dimensions = numGuards * 2 - Optimize entire set
    # Options:
    # c1 [0.5 to 2.5] = Cognitive parameter (high: more based on individual memory) 
    # c2 [0.5 to 2.5] = Social parameter (high: converge quickly)
    # w [0.4 to 1.2] = Inertia weight (high: explore more wider space)
    
    optimizer = ps.single.GlobalBestPSO(n_particles=numGuards, dimensions=num_dimensions,
                                        options={'c1': 1.2, 'c2': 0.3, 'w': 1.0},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))

    max_iters = 50
    no_improvement_limit = 5
    best_cost = cost
    best_pos = guard_positions
    no_improvement_count = 0

    for i in range(max_iters):
        cost, pos = optimizer.optimize(bsfScore, iters=1)

        if cost < best_cost:
            best_cost = cost
            positions = optimizer.swarm.position
            best_pos = np.array(positions).reshape(numGuards, num_dimensions)
            no_improvement_count = 0
        else:
            no_improvement_count += 1
     
        if no_improvement_count >= no_improvement_limit:
            print(f"Early stopping at iteration {i}", flush=True)
            break

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds", flush=True)    


    

    
