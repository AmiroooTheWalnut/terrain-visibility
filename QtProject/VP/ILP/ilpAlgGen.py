import argparse
import collections
import time
from pulp import LpMinimize, LpProblem, LpVariable, LpBinary

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

    start_time = time.time()

    # Define the problem
    prob = LpProblem("Minimize_Guards", LpMinimize)

    # Define the guard variables: 1 if guard is used, 0 otherwise
    lpGuardArray = [LpVariable(f'g{i}', cat=LpBinary) for i in range(nGuard)]

    # Define the flow variables: continuous variables representing Path each edge
    # Fij > 0 if flow is from i to j
    # FNj should never be negative (flow is always from N to j)
    # FiS should never be negative (flow is always from i to S)
    lpFlowfromN = [LpVariable(f'FN_{crossNorth[j]}', lowBound=0, upBound=1, cat="Continuous") for j in range(len(crossNorth))]
    lpFlowtoS = [LpVariable(f'F{crossSouth[j]}_S', lowBound=0, upBound=1, cat="Continuous") for j in range(len(crossSouth))]
    # Only needs to use those with i < j to avoid duplication
    lpFlowArray = []
    for i in range(ccCount):
        for j in range(i+1, ccCount):
            if edgeArray[i][j]:
                lpFlowArray.append(LpVariable(f'F{i}_{j}', lowBound=-1, upBound=1, cat="Continuous"))

    # Debug print
    if verbose:
        print("----------Guard/Region Info----------")
        print("nGuard = " + str(nGuard))
        print("gcArray:")
        for i in range(nGuard):
            for j in range(nCompPG[i]):
                print(f"{i} = {gcArray[i][j]}") 
        print("nCompPG:")
        print(nCompPG[:nGuard])
        print("ccParent:")
        print(ccParent)
        print("edgeArray:")
        for i in range(ccCount):
            for j in range(MAX_CC):
                if edgeArray[i][j]:
                    print(f"Connected: {i}, {j}")
        print("crossNorth:")
        print(crossNorth)
        print("crossSouth:")
        print(crossSouth)
        print("----------LpVariables----------")
        print("lpGuardArray LpVariable:")
        print(lpGuardArray)
        print("lpFlowfromN LpVariable:")
        print(lpFlowfromN)
        print("lpFlowtoS LpVariable:")
        print(lpFlowtoS)
        print("lpFlowArray LpVariable:")
        print(lpFlowArray)

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
    for i in range(ccCount):
        constraint_expr = 0
        for var in lpFlowfromN:
            if var.name == f'FN_{i}':
                constraint_expr += var
        for var in lpFlowtoS:
            if var.name == f'F{i}_S':
                constraint_expr -= var
        for j in range(ccCount):
            for var in lpFlowArray:
                if var.name == f'F{i}_{j}':
                    constraint_expr -= var   
                elif var.name == f'F{j}_{i}':
                    constraint_expr += var         
        prob += constraint_expr == 0, "ConstraintAt"+str(i)
        if verbose:
            print(constraint_expr)
                	
    # Guard must be selected for the flow to be selected
    # If Fij is selected, then parent guards of Ci/Cj must be selected
    # Convention is that i < j.  The flow for i > j is duplicated.
    # FNi and FiS are never negative.
    for i in range(ccCount):
        k = ccParent[i]
        for var in lpFlowfromN:
            if var.name == f'FN_{i}':
                prob += var <= lpGuardArray[k], f'Constraint_N_{i}'
                if verbose:
                    print(f'{var} <= lpGuardArray{k}')
                    print(f'{var} >= -lpGuardArray{k}')
        for var in lpFlowtoS:
            if var.name == f'F{i}_S':
                prob += var <= lpGuardArray[k], f'Constraint_{i}_S'
                if verbose:
                    print(f'{var} <= lpGuardArray{k}')
                    print(f'{var} >= -lpGuardArray{k}')
        for j in range(i+1, ccCount):
            for var in lpFlowArray:
                if var.name == f'F{i}_{j}':
                    k = ccParent[i]
                    prob += var <= lpGuardArray[k], f'Constraint1_{i}_{j}_g{k}'
                    prob += var >= -lpGuardArray[k], f'Constraint1_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpGuardArray{k}')
                        print(f'{var} >= -lpGuardArray{k}')
                    k = ccParent[j]
                    prob += var <= lpGuardArray[k], f'Constraint2_{i}_{j}_g{k}'
                    prob += var >= -lpGuardArray[k], f'Constraint2_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpGuardArray{k}')
                        print(f'{var} >= -lpGuardArray{k}')
              
    # Solve the problem
    prob.solve()

    end_time = time.time()

    # ------------ Print output -------------
    print(f"Status: {prob.status}")    
    print("Non-zero flow values below:")    
    for var in lpGuardArray:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}")

    for var in lpFlowfromN:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}")

    for var in lpFlowtoS:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}")

    for var in lpFlowArray:
        if var.varValue != 0.0:
            print(f"Path {var.name}: {var.varValue}")
    
    print(f"Total Cost: {prob.objective.value()}")

    elapsed_time = end_time - start_time
    print(f"Time to execute algorithm = {elapsed_time:.2g} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ILP')
    parser.add_argument('INPUT', type=str, help="ilpExport.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    f = open(args.INPUT, 'r')

    run(f, args.verbose)
