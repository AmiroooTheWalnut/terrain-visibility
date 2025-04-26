#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF
from mlCommon import visibilitySum, best_move
from common import fibonacci_lattice, square_uniform, setupGraph
import pyswarms as ps
import time
import copy
import sys

lastGuards = []
lastComps = []

#---------------------------------------
# Score visibility
#---------------------------------------
def visScore(guard_positions):

    visTotal = visibilitySum(guard_positions, guardHt, radius, elev, keepNS, verbose)

    print(f"Visibility score = {visTotal}")
    return -visTotal  # Lower cost the better - Use visibility as the score
    
#---------------------------------------
# Score BSF
#---------------------------------------
def bsfScore(guard_positions, baseline=False):
    global lastGuards, lastComps

    # To be sure positions are integral as they are passed by the optimizer
    guard_positions=guard_positions.astype(int)

    # Strategically move the guards
    if baseline or (scoreBSF and keepNS):
        guard_positions = best_move(guard_positions, guardHt, radius, elev, lastGuards, lastComps, verbose)

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, elev, verbose)

    if ilp:
        cost = runILP(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)
    else:
        cost = runBSF(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    # Only need to store lastComp and lastGuards once to prevent increasing number of restored guards
    if baseline:
        lastComps = gComps.copy()
        lastGuards = gGuards.copy()
   
    print(f"ILP/BSF score = {cost}")

    return cost  # Lower cost the better - Use visibility as the score

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

    args = parser.parse_args()

    filename = args.name        # None if not provided
    radius = args.radius        # Default if not provided
    numGuards = args.numGuards  # Default if not provided
    guardHt = args.height       # Default if not provided
    ilp = args.ilp              # False if not provided
    squareUniform = args.square # False if not provided
    randomize = args.randomize  # False if not provided (Only applicable if squareUniform is true)
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided
    keepNS = args.keepNS        # False if not provided
    
    #-------------------
    # Other options
    scoreBSF = True
    #-------------------

    start_time = time.time()   

    # Read elevation
    elev = read_png(filename, verbose, enableShow)
    nrows, ncols = elev.shape

    # Initial guard positions determined by fibonacci lattice
    if squareUniform:
        guard_positions = square_uniform(numGuards, nrows, ncols, randomize)
        numGuards = guard_positions.shape[0] # numGuards must be perfect square
    else:
        guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    # Get a baseline
    score = bsfScore(guard_positions, baseline=True)

    # Define bounds for the guards to not exceed the elev
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
                                        options={'c1': 1.8, 'c2': 0.8, 'w': 0.4},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))

    max_iters = 500
    no_improvement_limit = 10
    best_cost = score
    best_pos = guard_positions
    no_improvement_count = 0

    for i in range(max_iters):
        if scoreBSF:
            cost, pos = optimizer.optimize(bsfScore, iters=1)
        else:
            cost, pos = optimizer.optimize(visScore, iters=1)

        print(f"Cost = {cost}", flush=True)

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

    if scoreBSF:
        score = best_cost
    else:
        scoreBSF = True # KeepNS positions as original
        score = bsfScore(best_pos)
    print(f"Best position score = {score}", flush=True)

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds", flush=True)    


    

    
