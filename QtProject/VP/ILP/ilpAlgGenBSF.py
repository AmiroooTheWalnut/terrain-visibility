import argparse
import numpy as np
import time
from TerrainInput import classComp, classGuard, readInput

'''
-------------------------------------------------------------------------------------
Control Experiment of ilpAlgGen
-- This algorithm uses the same BSF algorithm as in the appVP
-------------------------------------------------------------------------------------

'''

def run(f, verbose):    
    gGuards, gComps, gNorths, gSouths = readInput(f, verbose)

    start_time = time.time()

    MAX_FRONTIERS = 30
    MAX_CC_PER_FRONTIER = 100

    nFrontiers = 0
    nCCPerFrontier = [0] * MAX_FRONTIERS  # Number of CC in each Frontier
    frontier = np.zeros((MAX_FRONTIERS, MAX_CC_PER_FRONTIER), dtype=int) # CC indices in each Frontier
    ccUsedForFrontier = [0] * len(gComps) # Flag set if cc is picked already
    ccIntersect1 = [] # Intersecting CC in the Frontier
    ccIntersect2 = [] # Intersecting CC in the Frontier

    # F0
    count = 0
    for cc in gNorths:
        ccUsedForFrontier[cc] = 1
        frontier[0][count] = cc
        count += 1
    nCCPerFrontier[0] = count

    if verbose:
        print("F0:")
        for i in range(nCCPerFrontier[0]):
            print(frontier[0][i])

    nFrontier = 1
    success = True

    # Subsequent frontiers
    returningPath = []
    done = False
    while done == False and success == True:
        assert nFrontier < MAX_FRONTIERS, "Too many frontiers"
        success = False
        if verbose:
            print(f"F{nFrontier}")

        # Loop through all the CC, check all the unmarked CC
        for guard in gGuards:
            for comp in guard.comps:
                cc = comp.id
                if verbose:
                    print(f"Checking {cc} for new Frontier")
                
                if ccUsedForFrontier[cc] == 0:

                    count = nCCPerFrontier[nFrontier]
                    assert count < MAX_CC_PER_FRONTIER, "Too many connected components per frontier"

                    # Loop through the CC from last frontier to check edgeArray for intersection
                    # Add the current CC to the current Frontier there is intersection with any CC 
                    # from the last frontier
                    for i in range(nCCPerFrontier[nFrontier-1]): 
                        dd = frontier[nFrontier-1][i]
                        if verbose:
                            print(f"Checking {dd} from last Frontier")
                        if dd in comp.intersects:
                            if verbose:
                                print(f"Component {cc} intersects Component {dd} from last Frontier")
                            # remember the intersecting CC
                            ccIntersect1.append(cc)
                            ccIntersect2.append(dd)
                            frontier[nFrontier][count] = cc

                            ccUsedForFrontier[cc] = 1
                            success = True
                            nCCPerFrontier[nFrontier] += 1

                            if cc in gSouths:
                                if verbose:
                                    print(f"Intersecting South")
                                done = True
                                returningPath.append(cc)
                            break

                    if done:
                        print(f"Done1 here {cc}, {dd}, {done}, {success}")
                        break
                if done:
                    break
            if done:
                break

        if success:                 
            nFrontier += 1
            
    # Build returningPath
    assert len(returningPath) > 0, "No solution exists!"

    end_time = time.time()

    # ------------ Print output -------------
    print("Building returningPath")
    done = False     # Done if there is no intersection
    cc = returningPath[-1]    
    while done == False:
        for i in range(len(ccIntersect1)):
            if cc == ccIntersect1[i]:
                dd = ccIntersect2[i]
                returningPath.append(dd)
                cc = returningPath[-1]
                break
        else:
            done = True
                
    # Print returningPath:
    print("Returning Path:")
    for cc in returningPath:
        print(f"Guard/Comp: {gComps[cc].parentID}, {cc}")
    print("Frontier Details:")
    for i in range(nFrontier):
        print(f"Frontier: {i}")
        for j in range(nCCPerFrontier[i]):
            print(f"Guards: {gComps[frontier[i][j]].parentID}")

    elapsed_time = end_time - start_time
    print(f"Time to execute algorithm = {elapsed_time:.2g} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ILP')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')

    run(f, args.verbose)
