import argparse
import time
from pulp import LpMinimize, LpProblem, LpVariable, LpBinary
from TerrainInput import classComp, classGuard, readInput

'''
-------------------------------------------------------------------------------------
Control Experiment of ilpAlgGen
-- This algorithm optimizes the number of Connected Components
-------------------------------------------------------------------------------------
g0, ..., gn-1 are integers, 0 = not selected, 1 = selected
Nodes: (CN = Component North, CS = Component South)

For each gi, a list of connected components with unique indices belong to it.
Each connected component has a list of intersecting components.
(See format in file ilpExport*.txt)

Fij are floats, 0 = not selected, Non-zero = selected
i, j are 0 to m-1

Minimize Sum(cci)

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

def runILP(f, verbose=False):    
    gGuards, gComps, gNorths, gSouths = readInput(f, verbose)

    start_time = time.time()

    # Define the problem
    prob = LpProblem("Minimize_Guards", LpMinimize)

    # Define the connected component variables: 1 if cc is used, 0 otherwise
    lpCCArray = [LpVariable(f'cc{i}', cat=LpBinary) for i in range(len(gComps))]

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
        print("----------LpVariables----------")
        print("lpCCArray LpVariable:")
        print(lpCCArray)
        print("lpFlowfromN LpVariable:")
        print(lpFlowfromN)
        print("lpFlowtoS LpVariable:")
        print(lpFlowtoS)
        print("lpFlowArray LpVariable:")
        print(lpFlowArray)

    # Define the objective function: Minimize the total cost
    prob += sum(lpCCArray)

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
        if verbose:
            print(constraint_expr)
                	
    # Guard must be selected for the flow to be selected
    # If Fij is selected, then parent guards of Ci/Cj must be selected
    # Convention is that i < j.  The flow for i > j is duplicated.
    # FNi and FiS are never negative.
    for i in range(len(gComps)):
        k = gComps[i].parentID
        for var in lpFlowfromN:
            if var.name == f'FN_{i}':
                prob += var <= lpCCArray[i], f'Constraint_N_{i}'
                if verbose:
                    print(f'{var} <= lpCCArray{i}')
                    print(f'{var} >= -lpCCArray{i}')
        for var in lpFlowtoS:
            if var.name == f'F{i}_S':
                prob += var <= lpCCArray[i], f'Constraint_{i}_S'
                if verbose:
                    print(f'{var} <= lpCCArray{i}')
                    print(f'{var} >= -lpCCArray{i}')
        for j in range(i+1, len(gComps)):
            for var in lpFlowArray:
                if var.name == f'F{i}_{j}':
                    prob += var <= lpCCArray[i], f'Constraint1_{i}_{j}_g{k}'
                    prob += var >= -lpCCArray[i], f'Constraint1_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpCCArray{i}')
                        print(f'{var} >= -lpCCArray{i}')
                    prob += var <= lpCCArray[j], f'Constraint2_{i}_{j}_g{k}'
                    prob += var >= -lpCCArray[j], f'Constraint2_{i}_{j}_g{k}_'
                    if verbose:
                        print(f'{var} <= lpCCArray{j}')
                        print(f'{var} >= -lpCCArray{j}')
              
    # Solve the problem
    prob.solve()

    end_time = time.time()

    # ------------ Print output -------------
    print(f"Status: {prob.status}")    
    print("Non-zero flow values below:")    
    for var in lpCCArray:
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

    runILP(f, args.verbose)
