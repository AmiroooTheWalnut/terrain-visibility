# ---------------------------------------
# Algorithm optimization without Machine Learning
# ---------------------------------------
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF
from ilpAlgGen import runILP
from common import fibonacci_lattice, square_uniform, setupGraph, pairGuards
import time
import sys

#---------------------------------------
# guard_positions is being passed as 1-D array
#---------------------------------------
def bsfScore(guard_positions, pairGuardFlag=False, verbose=False, enableShow=False):

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, bitmap, verbose)
    
    if pairGuardFlag:
        pairGuards(nrows, ncols, gGuards, gComps, gNorths, gSouths, verbose)

    score = runBSF(ncols, nrows, bitmap, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    print(f"Number of Frontier = {score}")

    return score # Lower cost the better

#---------------------------------------
# guard_positions is being passed as 1-D array
#---------------------------------------
def ilpScore(guard_positions, pairGuardFlag=False, verbose=False, enableShow=False):

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, bitmap, verbose)

    if pairGuardFlag:
        pairGuards(nrows, ncols, gGuards, gComps, gNorths, gSouths, verbose)
    
    score = runILP(ncols, nrows, bitmap, gGuards, gComps, gNorths, gSouths, verbose, enableShow)

    print(f"Number of Guards = {score}")

    return score # Lower cost the better

if __name__ == "__main__":
    sys.stdout = open('opMainLog.txt', 'a')
    print("=============opMain.py Run Start===============")

    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--height', type=int, help="10")
    parser.add_argument('--ilp', action='store_true', help="Run ILP")
    parser.add_argument('--square', action='store_true', help="Square uniform")
    parser.add_argument('--randomize', action='store_true', help="Randomize Square Pos")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing terrain")

    args = parser.parse_args()

    filename = args.name        # Default if not provided
    radius = args.radius        # Default if not provided
    numGuards = args.numGuards  # Default if not provided
    guardHt = args.height       # Default if not provided
    ilp = args.ilp              # False if not provided
    squareUniform = args.square # False if not provided
    randomize = args.randomize  # False if not provided (Only applicable if squareUniform is true)
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    # Other options not configurable from input
    # ----------------
    pairGuardFlag = False # Testing special pairing logic
    # ----------------

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

    if ilp:
        score = ilpScore(guard_positions, pairGuardFlag, verbose, enableShow)
        print(f"ILP yielded number of guards = {score}")
    else:     
        score = bsfScore(guard_positions, pairGuardFlag, verbose, enableShow)
        print(f"BSF yielded number of frontiers = {score}")

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    
