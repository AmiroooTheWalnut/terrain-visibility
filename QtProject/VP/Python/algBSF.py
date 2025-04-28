import argparse
import numpy as np
import time
from TerrainInput import classComp, classGuard, readInput
from common import vprint, elapsed
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

NO_SOLUTION = 9999
MAX_FRONTIERS = 100
MAX_CC_PER_FRONTIER = 500

# ---------------------------------
# Show frontiers
# ---------------------------------
def show_frontiers(bitmap, gGuards, gComps, nFrontier, nCCPerFrontier, frontier):

    nrows, ncols = bitmap.shape
    light_gray = np.array([200 / 255.0] * 3, dtype=np.float32)
    colors = np.full((nrows, ncols, 3), light_gray)
    
    for i in range(nFrontier): 
        col = np.random.rand(3,)
        for n in range(nCCPerFrontier[i]):
            id = frontier[i][n]
            comp = gComps[id]
            for connectedRow in comp.connectedRows:
                colors[connectedRow[0]][connectedRow[1]:connectedRow[2]+1] = col

    # Show guard positions
    col = np.array([255,255,255]) / 255.0 # White
    for guard in gGuards:
        for x in range(-5,5):
            for y in range(-5,5):
                a = guard.col+x
                b = guard.row+y
                if a >= 0 and a < ncols and b >= 0 and b < nrows:
                    colors[b][a] = col
        
    x = np.arange(ncols)
    y = np.arange(nrows)
    x, y = np.meshgrid(x, y)

    # Create a 3D plot
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the bitmap as the Z axis, set strides to larger number for speed
    ax.plot_surface(x, y, bitmap, facecolors=colors, shade=False, rstride=3, cstride=3, antialiased=True)
    ax.set_zlim(0, 500)
    ax.view_init(elev=30, azim=225)  # Rotate view to focus on (0,0,0)

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.text(x=200, y=200, z=400, s=f"BSF Result: {nFrontier} frontiers", color='black', fontsize=12)

    # Show the plot
    plt.show()

# ---------------------------------
# BSF - Same as in appVP
# ---------------------------------
def runBSF(bitmap, gGuards, gComps, gNorths, gSouths, verbose=False, enableShow=False):

    # No solution if North or South borders do not overlap with any CC
    if len(gNorths) == 0 or len(gSouths) == 0:
        print("No North/South intersection!", flush=True)
        return NO_SOLUTION

    timestamp = time.time()

    ccUsedForFrontier = [0] * len(gComps) # Flag set if cc is picked already
    ccIntersect1 = [] # Intersecting CC in the Frontier
    ccIntersect2 = [] # Intersecting CC in the Frontier

    # Reset global variables
    nFrontier = 0
    nCCPerFrontier = [0] * MAX_FRONTIERS  # Number of CC in each Frontier
    frontier = np.zeros((MAX_FRONTIERS, MAX_CC_PER_FRONTIER), dtype=int) # CC indices in each Frontier

    # F0
    count = 0
    for cc in gNorths:
        ccUsedForFrontier[cc] = 1
        frontier[0][count] = cc
        count += 1
    nCCPerFrontier[0] = count

    if verbose:
        print("F0:", flush=True)
        for i in range(nCCPerFrontier[0]):
            print(frontier[0][i], flush=True)

    nFrontier = 1
    success = True

    # Subsequent frontiers
    returningPath = []
    done = False
    while done == False and success == True:
        assert nFrontier < MAX_FRONTIERS, "Too many frontiers"
        success = False
        vprint(verbose, f"F{nFrontier}", flush=True)

        # Loop through all the CC, check all the unmarked CC
        for guard in gGuards:
            for cc in guard.compIDs:
                comp = gComps[cc]
                #vprint(verbose, f"Checking {cc} for new Frontier", flush=True)
                
                if ccUsedForFrontier[cc] == 0:

                    count = nCCPerFrontier[nFrontier]
                    assert count < MAX_CC_PER_FRONTIER, "Too many connected components per frontier"

                    # Loop through the CC from last frontier to check edgeArray for intersection
                    # Add the current CC to the current Frontier there is intersection with any CC 
                    # from the last frontier
                    for i in range(nCCPerFrontier[nFrontier-1]): 
                        dd = frontier[nFrontier-1][i]
                        #vprint(verbose, f"Checking {dd} from last Frontier", flush=True)
                        if dd in comp.intersects:
                            #vprint(verbose, f"Component {cc} intersects Component {dd} from last Frontier", flush=True)
                            # remember the intersecting CC
                            ccIntersect1.append(cc)
                            ccIntersect2.append(dd)
                            frontier[nFrontier][count] = cc

                            ccUsedForFrontier[cc] = 1
                            success = True
                            nCCPerFrontier[nFrontier] += 1

                            if cc in gSouths:
                                #vprint(verbose, f"Intersecting South", flush=True)
                                done = True
                                returningPath.append(cc)
                                comp.selected = True
                            break

                    if done:
                        break
                if done:
                    break
            if done:
                break

        if success:                 
            nFrontier += 1
            
    timestamp = elapsed(verbose, timestamp, "Time to execute BSF algorithm")

    # Build returningPath
    # assert len(returningPath) > 0, "No solution exists!"
    if len(returningPath) == 0:
        print("No solution exists!", flush=True)
        nFrontier = NO_SOLUTION 
    else:
        # ------------ Print output -------------
        #print("Building returningPath", flush=True)
        done = False     # Done if there is no intersection
        cc = returningPath[-1]    
        while done == False:
            for i in range(len(ccIntersect1)):
                if cc == ccIntersect1[i]:
                    dd = ccIntersect2[i]
                    returningPath.append(dd)
                    gComps[dd].selected = True
                    cc = returningPath[-1]
                    break
            else:
                done = True
                

        if verbose:
            # Print returningPath:
            print("---------- Returning Path ----------------", flush=True)
            for cc in returningPath:
                print(f"Guard/Comp: {gComps[cc].parentID}, {cc}", flush=True)

            print("Frontier Details:", flush=True)
            for i in range(nFrontier):
                print(f"Frontier: {i}", flush=True)
                for j in range(nCCPerFrontier[i]):
                    comp = gComps[frontier[i][j]]
                    print(f"Component: {comp.id}, Guards: {comp.parentID}", flush=True)

        if enableShow:
            show_frontiers(bitmap, gGuards, gComps, nFrontier, nCCPerFrontier, frontier)
    
    return nFrontier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BSF')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')
    verbose = args.verbose

    gGuards, gComps, gNorths, gSouths = readInput(f, verbose)
    nFrontier = runBSF(None, gGuards, gComps, gNorths, gSouths, verbose) # No bitmap when input is text file
    print(f"Number of Connected Components needed = {nFrontier}", flush=True)
