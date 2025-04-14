# ---------------------------------------
# Algorithm optimization without Machine Learning
# ---------------------------------------
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF, show_frontiers
from common import fibonacci_lattice, square_uniform, setupGraph, pairGuards
import time

#---------------------------------------
# guard_positions is being passed as 1-D array
#---------------------------------------
def bsfScore(guard_positions, pairGuardFlag=False, verbose=False):

    gGuards, gComps, gNorths, gSouths = setupGraph(guard_positions, guardHt, radius, bitmap, verbose)
    
    if pairGuardFlag:
        pairGuards(nrows, ncols, gGuards, gComps, gNorths, gSouths, verbose)

    score = runBSF(gGuards, gComps, gNorths, gSouths, verbose)
    #score = runILP(gGuards, gComps, gNorths, gSouths, verbose)

    # No show on GPU
    #if enableShow:
    #    show_frontiers(nrows, ncols, bitmap, gGuards, gComps)

    print(f"Number of Frontier = {score}")

    return score # Lower cost the better

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")

    args = parser.parse_args()
    filename = args.name        # None if not provided
    radius = args.radius        # None if not provided
    numGuards = args.numGuards  # None if not provided
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    # Other options
    # ----------------
    guardHt = 10     # Guard height above terrain
    squareUniform = True
    randomize = False
    pairGuardFlag = True
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

    bsfScore(guard_positions, pairGuardFlag, verbose)

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    
