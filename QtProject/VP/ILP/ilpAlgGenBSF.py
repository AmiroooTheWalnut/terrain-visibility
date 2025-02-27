import argparse
import collections
import numpy as np
import time

'''
-------------------------------------------------------------------------------------
Control Experiment of ilpAlgGen
-- This algorithm uses the same BSF algorithm as in the appVP
-------------------------------------------------------------------------------------

'''

def run(f, verbose):    
    nGuard = 0  # Number of guards
    gcArray = []  # Guard * Connected Components
    ccParent = [] # Reverse lookup from CC to Guard number
    nCompPG = []  # Number of CC per guard
    edgeArray = collections.defaultdict(lambda: collections.defaultdict(int)) # indexed by cc * cc, 1 = intersect, 0 = no intersect
    crossNorth = [] # Array of cc that crosses North
    crossSouth = [] # Array of cc that crosses South
    ccCount = 0 # Total connected components
    guardnum = -1
 
    # Read input file and build the connectedness map
    for l in f.readlines():
        typeStr, numStr = l.split()
        num = int(numStr)

        if typeStr == "Guard":
            #print("Got guard = " + str(num))
            guardnum = num
            nCompPG.append(0) # Got a new guard
            gcArray.append([]) # Got a new guard
            nGuard += 1
        elif typeStr == "ConnectedComponent":
            #print("Got cc = " + str(num))
            gcArray[guardnum].append(num) # Connected Component index
            nCompPG[guardnum] += 1
            ccParent.append(guardnum)
            ccCount += 1
        elif typeStr == "Intersecting":
            #print("Got intersection = " + str(num))
            edgeArray[ccCount-1][num] = 1
        elif typeStr == "CrossNorth":
            #print("Got north = " + str(num))
            crossNorth.append(num)
        elif typeStr == "CrossSouth":
            #print("Got sourth = " + str(num))
            crossSouth.append(num)
        else:
            raise Exception("Uncognized type!")

    if len(crossNorth) == 0 or len(crossSouth) == 0:
        print("There is no north-crossing or no south-crossing connected components!")
        return

    MAX_FRONTIERS = 30
    MAX_CC_PER_FRONTIER = 100

    nFrontiers = 0
    nCCPerFrontier = [0] * MAX_FRONTIERS  # Number of CC in each Frontier
    frontier = np.zeros((MAX_FRONTIERS, MAX_CC_PER_FRONTIER), dtype=int) # CC indices in each Frontier
    ccUsedForFrontier = [0] * len(ccParent) # Flag set if cc is picked already
    ccIntersect1 = [] # Intersecting CC in the Frontier
    ccIntersect2 = [] # Intersecting CC in the Frontier

    start_time = time.time()

    # F0
    for cc in crossNorth:
        ccUsedForFrontier[cc] = 1
        count = nCCPerFrontier[0]
        frontier[0][count] = cc
        nCCPerFrontier[0] += 1

    if verbose:
        print("F0:")
        for i in range(nCCPerFrontier[0]):
            print(frontier[0][i])

    nFrontier = 1
    success = True

    # Subsequent frontiersf
    returningPath = []
    done = False
    while done == False and success == True:
        assert nFrontier < MAX_FRONTIERS, "Too many frontiers"
        success = False
        if verbose:
            print(f"F{nFrontier}")

        # Loop through all the CC, check all the unmarked CC
        for k in range(nGuard):
            for i in range(nCompPG[k]):

                cc = gcArray[k][i]
                
                if verbose:
                    print(f"Checking Connected Component {cc}")

                if ccUsedForFrontier[cc] == 0:

                    count = nCCPerFrontier[nFrontier]
                    assert count < MAX_CC_PER_FRONTIER, "Too many connected components per frontier"

                    # Loop through the CC from last frontier to check edgeArray for intersection
                    # Add the current CC to the current Frontier there is intersection with any CC 
                    # from the last frontier
                    for i in range(nCCPerFrontier[nFrontier-1]): 
                        dd = frontier[nFrontier-1][i]
                        if verbose:
                            print(f"Checking Connected Component {dd} from last Frontier {nFrontier-1}")
                        if edgeArray[cc][dd] == 1:
                            if verbose:
                                print("Intersected")
                            # remember the intersecting CC
                            ccIntersect1.append(cc)
                            ccIntersect2.append(dd)
                            frontier[nFrontier][count] = cc

                            ccUsedForFrontier[cc] = 1
                            success = True
                            nCCPerFrontier[nFrontier] += 1

                            if cc in crossSouth:
                                if verbose:
                                    print(f"Intersecting South")
                                done = True
                                returningPath.append(cc)
                            break

                    if done or success:
                        break
                if done:
                    break
            if done:
                break

        if success:                 
            nFrontier += 1
            
    # Build returningPath
    if len(returningPath) == 0:
        print("No solution exists!")

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
        print(f"Guard: {ccParent[cc]}")
    print("Frontier Details:")
    for i in range(nFrontier):
        print(f"Frontier: {i}")
        for j in range(nCCPerFrontier[i]):
            print(f"Guards: {ccParent[frontier[i][j]]}")

    elapsed_time = end_time - start_time
    print(f"Time to execute algorithm = {elapsed_time:.2g} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ILP')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')

    run(f, args.verbose)
