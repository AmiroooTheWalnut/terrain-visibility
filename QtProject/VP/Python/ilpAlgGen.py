import argparse
import time
import numpy as np
import re
from pulp import LpMinimize, LpProblem, LpVariable, LpBinary
from TerrainInput import classComp, classGuard, readInput
from common import vprint, elapsed
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

'''
g0, ..., gn-1 are integers, 0 = not selected, 1 = selected
Nodes: (CN = Component North, CS = Component South)

For each gi, a list of connected components with unique indices belong to it.
Each connected component has a list of intersecting components.
(See format in file ilpExport*.txt)

Fij are floats, 0 = not selected, Non-zero = selected
i, j are 0 to m-1

Minimize Sum(gi)

-gk <= fij <= gk, for all k, i, j where gk is the parent of ci

-1 <= xij = direction from Node i to Node j <= 1,

For all i, sum of xij and sum of xki = 0, for all j and k

Sum of FNi = 1, N = North node, for all i
Sum of FjS = 1, for all j, S = South node

Directed Edges:
    CN and CS only goes one way
    So duplicates are removed
    For convention and to avoid missing edges, 2nd index is always > 1st index

    CN-Ci if Ci overlaps North
    Cj-CS if Cj overlaps South
    Ci-Cj if Ci overlaps j and i < j

'''
# ---------------------------------
# Show ilp solution
# ---------------------------------
def show_ilp(bitmap, gGuards, gComps, lpFlowArray, nGuards):

    nrows, ncols = bitmap.shape
    light_gray = np.array([200 / 255.0] * 3, dtype=np.float32)
    colors = np.full((nrows, ncols, 3), light_gray)
    
    # This will plot one component an extra time if we don't keep track
    plotted = []
    for var in lpFlowArray:
        if var.varValue != 0.0:
            ids = re.findall(r'\d+', var.name)
            for id in ids:
                n = int(id)
                if (n in plotted) == False:
                    col = np.random.rand(3,)
                    comp = gComps[n]
                    for connectedRow in comp.connectedRows:
                        colors[connectedRow[0]][connectedRow[1]:connectedRow[2]+1] = col
                    plotted.append(n)

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

    # Plot the bitmap as the Z axis, set strides to larger  number for speed
    ax.plot_surface(x, y, bitmap, facecolors=colors, shade=False, rstride=3, cstride=3, antialiased=True)
    ax.set_zlim(0, 500)
    ax.view_init(elev=30, azim=225)  # Rotate view to focus on (0,0,0)

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.text(x=200, y=200, z=400, s=f"ILP Result: {nGuards} guards, {len(plotted)} components", color='black', fontsize=12)

    # Show the plot
    plt.show()

def runILP(bitmap, gGuards, gComps, gNorths, gSouths, verbose=False, enableShow=False):
    # No solution if North or South borders do not overlap with any CC
    if len(gNorths) == 0 or len(gSouths) == 0:
        print("No North/South intersection!", flush=True)
        return 9999

    timestamp = time.time()

    # Define the problem
    prob = LpProblem("Minimize_Guards", LpMinimize)

    # Define the guard variables: 1 if guard is used, 0 otherwise
    lpGuardArray = [LpVariable(f'g{i}', cat=LpBinary) for i in range(len(gGuards))]

    # Define the flow variables: continuous variables representing Path each edge
    # Fij > 0 if flow is from i to j
    # FNj should never be negative (flow is always from N to j)
    # FiS should never be negative (flow is always from i to S)
    lpFlowfromN = [LpVariable(f'FN_{gNorths[j]}', lowBound=0, upBound=1, cat="Continuous") for j in range(len(gNorths))]
    lpFlowtoS = [LpVariable(f'F{gSouths[j]}_S', lowBound=0, upBound=1, cat="Continuous") for j in range(len(gSouths))]
    # Only needs to use those with i < j to avoid duplication
    lpFlowArray = []
    for i in range(len(gComps)):
        for j in range(i+1, len(gComps)):
            if j in gComps[i].intersects:
                lpFlowArray.append(LpVariable(f'F{i}_{j}', lowBound=-1, upBound=1, cat="Continuous"))

    # Debug print
    if verbose:
        print("----------LpVariables----------", flush=True)
        print("lpGuardArray LpVariable:", flush=True)
        print(lpGuardArray, flush=True)
        print("lpFlowfromN LpVariable:", flush=True)
        print(lpFlowfromN, flush=True)
        print("lpFlowtoS LpVariable:", flush=True)
        print(lpFlowtoS, flush=True)
        print("lpFlowArray LpVariable:", flush=True)
        print(lpFlowArray, flush=True)

    # Define the objective function: Minimize the total cost
    prob += sum(lpGuardArray)

    # Define the constraints:
    # At North/South, from N to i, and from j to S
    prob += sum(lpFlowfromN) == 1, "ConstraintAtN"
    prob += sum(lpFlowtoS) == 1, "ConstraintAtS"

    # Other nodes j: Sum Fij = 0 for all i
    # Flip sign if Fij is defined as Fji
    # At each vertex, sum of all flows into/out of the vertex = 0
    # Only use the lpFlowArray index with i < j
    for i in range(len(gComps)):
        constraint_expr = 0
        for var in lpFlowfromN:
            if var.name == f'FN_{i}':
                constraint_expr += var
        for var in lpFlowtoS:
            if var.name == f'F{i}_S':
                constraint_expr -= var
        for j in range(len(gComps)):
            for var in lpFlowArray:
                if var.name == f'F{i}_{j}':
                    constraint_expr -= var   
                elif var.name == f'F{j}_{i}':
                    constraint_expr += var         
        prob += constraint_expr == 0, "ConstraintAt"+str(i)
        vprint(verbose, constraint_expr, flush=True)
                	
    # Guard must be selected for the flow to be selected
    # If Fij is selected, then parent guards of Ci/Cj must be selected
    # Convention is that i < j.  The flow for i > j is duplicated.
    # FNi and FiS are never negative.
    for i in range(len(gComps)):
        k = gComps[i].parentID
        for var in lpFlowfromN:
            if var.name == f'FN_{i}':
                prob += var <= lpGuardArray[k], f'Constraint_N_{i}'
                if verbose:
                    print(f'{var} <= lpGuardArray{k}', flush=True)
                    print(f'{var} >= -lpGuardArray{k}', flush=True)
        for var in lpFlowtoS:
            if var.name == f'F{i}_S':
                prob += var <= lpGuardArray[k], f'Constraint_{i}_S'
                if verbose:
                    print(f'{var} <= lpGuardArray{k}', flush=True)
                    print(f'{var} >= -lpGuardArray{k}', flush=True)
        for j in range(i+1, len(gComps)):
            for var in lpFlowArray:
                if var.name == f'F{i}_{j}':
                    k = gComps[i].parentID
                    prob += var <= lpGuardArray[k], f'Constraint1_{i}_{j}_g{k}'
                    prob += var >= -lpGuardArray[k], f'Constraint1_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpGuardArray{k}', flush=True)
                        print(f'{var} >= -lpGuardArray{k}', flush=True)
                    k = gComps[j].parentID
                    prob += var <= lpGuardArray[k], f'Constraint2_{i}_{j}_g{k}'
                    prob += var >= -lpGuardArray[k], f'Constraint2_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpGuardArray{k}', flush=True)
                        print(f'{var} >= -lpGuardArray{k}', flush=True)
              
    # Solve the problem
    prob.solve()

    timestamp = elapsed(verbose, timestamp, "Time to execute ILP algorithm")

    # ------------ Print output -------------
    print(f"Status: {prob.status}", flush=True)    
    print("Non-zero flow values below:", flush=True)    
    for var in lpGuardArray:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}", flush=True)

    for var in lpFlowfromN:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}", flush=True)

    for var in lpFlowtoS:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}", flush=True)

    for var in lpFlowArray:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}", flush=True)
    
    print(f"Total Cost: {prob.objective.value()}", flush=True)

    if enableShow:
        show_ilp(bitmap, gGuards, gComps, lpFlowArray, int(prob.objective.value()))

    return int(prob.objective.value())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ILP')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')
    verbose = args.verbose

    gGuards, gComps, gNorths, gSouths = readInput(f, verbose)

    num = runILP(None, gGuards, gComps, gNorths, gSouths, verbose) # No bitmap when input is text file
    print(f"Number of Guards needed = {num}", flush=True)
