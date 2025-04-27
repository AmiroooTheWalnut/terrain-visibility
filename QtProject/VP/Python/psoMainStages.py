#---------------------------------------
# Particle Swarm Optimization 
# Stage 1: Maximimize visibility/diameter (Keeping N/S)
# Stage 2: Maximimize connectedness (Keeping N/S) 
# Stage 3: Optimize solution (Keeping N/S and previous connectedness of shortest path)
#---------------------------------------
import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF
from ilpAlgGen import runILP
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
def visScore(guard_positions, diam=False):

    visTotal = visibilitySum(guard_positions, guardHt, radius, elev, optDiam, keepNS, verbose)

    print(f"Visibility score = {visTotal}")
    return -visTotal  # Lower cost the better - Use visibility as the score
    
#---------------------------------------
# Score connectedness
#---------------------------------------
def connectScore(guard_positions):
    global lastGuards, lastComps

    # To be sure positions are integral as they are passed by the optimizer
    guard_positions=guard_positions.astype(int)

    # Strategically move the guards
    if keepNS:
        guard_positions = best_move(guard_positions, guardHt, radius, elev, lastGuards, lastComps, verbose)

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, elev, verbose)

    if ilp:
        cost = runILP(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)
    else:
        cost = runBSF(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    # Only need to store lastComp and lastGuards once to prevent increasing number of restored guards
    if keepNS:
        lastComps = gComps.copy()
        lastGuards = gGuards.copy()
   
    print(f"ILP/BSF score = {cost}")

    return cost  # Lower cost the better - Use visibility as the score
#---------------------------------------
# Score BSF/ILP
#---------------------------------------
def bsf_ilp_Score(guard_positions, baseline=False):
    global lastGuards, lastComps

    # To be sure positions are integral as they are passed by the optimizer
    guard_positions=guard_positions.astype(int)

    # Strategically move the guards after first time
    if keepNS and (not baseline):
        guard_positions = best_move(guard_positions, guardHt, radius, elev, lastGuards, lastComps, verbose)

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, elev, verbose)

    if ilp:
        cost = runILP(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)
    else:
        cost = runBSF(elev, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    # Only need to store lastComp and lastGuards once to prevent increasing number of restored guards
    if baseline:
        lastGuards = []
        lastComps = []
        lastComps = gComps.copy()
        lastGuards = gGuards.copy()
   
    print(f"ILP/BSF score = {cost}")

    return cost  # Lower cost the better - Use visibility as the score

if __name__ == "__main__":
    sys.stdout = open('psoMainStagesLog.txt', 'a')
    print("=============psoMainStages.py Run Start===============", flush=True)

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

    # -------------------------------
    # Other options
    optDiam = False # If set, we optimize diameter instead of area
    # -------------------------------    

    start_time = time.time()   

    # Read elevation
    elev = read_png(filename, verbose, enableShow)
    nrows, ncols = elev.shape

    # --------------------------------
    # Initial guard positions determined by fibonacci lattice
    # --------------------------------
    if squareUniform:
        guard_positions = square_uniform(numGuards, nrows, ncols, randomize)
        numGuards = guard_positions.shape[0] # numGuards must be perfect square
    else:
        guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    # --------------------------------
    # Set up PSO
    # c1 [0.5 to 2.5] = Cognitive parameter (high: more based on individual memory) 
    # c2 [0.5 to 2.5] = Social parameter (high: converge quickly)
    # w [0.4 to 1.2] = Inertia weight (high: explore more wider space)    
    # --------------------------------

    # Define bounds for the guards to not exceed the elev
    num_dimensions = 2
    lb = np.array([0, 0])
    ub = np.array([nrows-1, ncols-1])
    optimizer = ps.single.GlobalBestPSO(n_particles=numGuards, dimensions=num_dimensions,
                                        options={'c1': 1.8, 'c2': 0.5, 'w': 1.2},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))
    max_iters = 500
    no_improvement_limit = 10
    no_solution_limit = 30

    # --------------------------------
    # Stage 1
    # --------------------------------
    no_improvement_count = 0
    no_solution_count = 0
    best_pos = guard_positions
    best_cost = visScore(guard_positions)  # Baseline
    for i in range(max_iters):
        cost, pos = optimizer.optimize(visScore, iters=1)
        print(f"visScore cost = {cost}", flush=True)
        if cost < best_cost:
            best_cost = cost
            positions = optimizer.swarm.position
            best_pos = np.array(positions).reshape(numGuards, num_dimensions)
            no_improvement_count = 0
        else:
            no_improvement_count += 1
     
        if no_improvement_count >= no_improvement_limit:
            print(f"visScore: Early stopping at iteration {i}: Cause is {no_improvement_limit} iterations with no improvement", flush=True)
            break

    # --------------------------------
    # Stage 2
    # --------------------------------
    no_improvement_count = 0
    no_solution_count = 0
    guard_positions = best_pos
    best_cost = connectScore(guard_positions)  # Baseline
    for i in range(max_iters):
        cost, pos = optimizer.optimize(connectScore, iters=1)
        print(f"connectScore cost = {cost}", flush=True)
        if cost < best_cost:
            best_cost = cost
            positions = optimizer.swarm.position
            best_pos = np.array(positions).reshape(numGuards, num_dimensions)
            no_improvement_count = 0
        else:
            no_improvement_count += 1
     
        if no_improvement_count >= no_improvement_limit:
            print(f"connectScore: Early stopping at iteration {i}: Cause is {no_improvement_limit} iterations with no improvement", flush=True)
            break

    # --------------------------------
    # Stage 3
    # --------------------------------
    no_improvement_count = 0
    no_solution_count = 0
    guard_positions = best_pos
    best_cost = bsf_ilp_Score(guard_positions)  # Baseline
    for i in range(max_iters):
        cost, pos = optimizer.optimize(bsf_ilp_Score, iters=1)
        print(f"bsf_ilp cost = {cost}", flush=True)

        if cost == 9999: # Only count those that have solutions
            no_solution_count += 1
        else:
            no_solution_count = 0
            if cost < best_cost:
                best_cost = cost
                positions = optimizer.swarm.position
                best_pos = np.array(positions).reshape(numGuards, num_dimensions)
                no_improvement_count = 0
            else:
                no_improvement_count += 1
     
        if no_improvement_count >= no_improvement_limit:
            print(f"Early stopping at iteration {i}: Cause is {no_improvement_limit} iterations with no improvement", flush=True)
            break
        if no_solution_count >= no_solution_limit:
            print(f"Early stopping at iteration {i}: Cause is {no_solution_limit} iterations with no solution", flush=True)
            break

    print(f"Best position score = {best_cost}", flush=True)

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds", flush=True)    


    

    
