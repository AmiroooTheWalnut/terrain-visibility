import argparse
import numpy as np
import time
from TerrainInput import classComp, classGuard, readInput
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

NO_SOLUTION = 9999
MAX_FRONTIERS = 30
MAX_CC_PER_FRONTIER = 500


# For display of frontiers
# Using global memory to show frontiers -- Won't work when running multi-threaded
# But we shouldn't be showing frontiers in multi-threaded executions anyway.
nFrontier = 0
nCCPerFrontier = [0] * MAX_FRONTIERS  # Number of CC in each Frontier
frontier = np.zeros((MAX_FRONTIERS, MAX_CC_PER_FRONTIER), dtype=int) # CC indices in each Frontier

# ---------------------------------
# Show frontiers
# ---------------------------------
def show_frontiers(width, height, array, gGuards, gComps):
    colors = np.zeros((width, height, 3))
    
    for i in range(nFrontier): 
        col = np.random.rand(3,)
        for n in range(nCCPerFrontier[i]):
            id = frontier[i][n]
            comp = gComps[id]
            for x in range(comp.minX, comp.maxX):
                for y in range(comp.minY, comp.maxY):
                    if comp.bitmap[x-comp.minX][y-comp.minY]:
                        colors[x][y] = col

    # Show guard positions
    col = np.array([255,255,255]) / 255.0 # White
    for guard in gGuards:
        for x in range(-5,5):
            for y in range(-5,5):
                a = guard.x+x
                b = guard.y+y
                if a >= 0 and a < width and b >= 0 and b < height:
                    colors[a][b] = col
        
    x = np.linspace(0, width-1, width)
    y = np.linspace(0, height-1, height)
    x, y = np.meshgrid(x, y)

    # Create a 3D plot
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the array as the Z axis
    ax.plot_surface(x, y, array, facecolors=colors)
    ax.set_zlim(0, 500)
    ax.view_init(elev=30, azim=225)  # Rotate view to focus on (0,0,0)

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.text(x=400, y=400, z=400, s=f"Number of frontiers = {nFrontier}", color='black', fontsize=12)

    # Show the plot
    plt.show()

# ---------------------------------
# BSF - Same as in appVP
# ---------------------------------
def runBSF(gGuards, gComps, gNorths, gSouths, verbose=False):

    # No solution if North or South borders do not overlap with any CC
    if len(gNorths) == 0 or len(gSouths) == 0:
        print("No North/South intersection!")
        return NO_SOLUTION

    if verbose:
        start_time = time.time()

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
            for cc in guard.compIDs:
                comp = gComps[cc]
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
                        break
                if done:
                    break
            if done:
                break

        if success:                 
            nFrontier += 1
            
    if verbose:
        end_time = time.time()
        print(f"Time to execute BSF algorithm = {end_time - start_time:.2g} seconds")

    # Build returningPath
    # assert len(returningPath) > 0, "No solution exists!"
    if len(returningPath) == 0:
        print("No solution exists!")
        nFrontier = NO_SOLUTION 
    else:
        # ------------ Print output -------------
        #print("Building returningPath")
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
                

        if verbose:
            # Print returningPath:
            print("---------- Returning Path ----------------")
            for cc in returningPath:
                print(f"Guard/Comp: {gComps[cc].parentID}, {cc}")

            print("Frontier Details:")
            for i in range(nFrontier):
                print(f"Frontier: {i}")
                for j in range(nCCPerFrontier[i]):
                    comp = gComps[frontier[i][j]]
                    print(f"Component: {comp.id}, Guards: {comp.parentID}")

    
    return nFrontier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BSF')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')
    verbose = args.verbose

    gGuards, gComps, gNorths, gSouths = readInput(f, verbose)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths, verbose)
    print(f"Number of Connected Components needed = {nFrontier}")
