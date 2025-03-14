import numpy as np
import argparse
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from Visibility import calc_vis
from ReadElevImg import read_png, show_terrain
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF

#---------------------------------------
# Function to generate Fibonacci lattice
#---------------------------------------
def fibonacci_lattice(n_points, nrows, ncols):
    gR = (1.0 + np.sqrt(5.0)) / 2.0

    points = []
    for count in range(n_points):
        x = float(count+1) / gR
        x -= int(x)
        y = float(count+1) / (n_points+1)
        points.append((int(x*nrows), int(y*ncols)))
    
    return points

#---------------------------------------
# Set Up
#---------------------------------------
def setup(filename, verbose):    
    bitmap = read_png(filename, verbose)
    nrows, ncols = bitmap.shape

    # Initial parameters and guard locations
    # Number of guards, height, radius, terrain bitmap, verbose
    numGuards = 100
    elev = 10     # Default = 10
    radius = 30  # Default = 123

    lattice_points = fibonacci_lattice(numGuards, nrows, ncols)
    x_coords, y_coords = zip(*lattice_points)

    for guardnum in range(numGuards):
        guard = classGuard(guardnum)
        gGuards.append(guard)
        guard.setLocation(x_coords[guardnum], y_coords[guardnum], elev, radius) 
    
        #viewshed is what this guard can see (1 = yes, 0 = no)
        viewshed = calc_vis(guard, bitmap, verbose)  
	
	# Find the Connected Components per guard
        findConnected(guard, viewshed, verbose)

    # Determine the intersections of the Connected Components
    findIntersections(verbose)
    printGuards(verbose)

#---------------------------------------
# Reinforcement Learning
#---------------------------------------
def train(verbose):

    # Perform BSF
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths, verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('INPUT', type=str, help="test.png")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    args = parser.parse_args()
   
    setup(args.INPUT, args.verbose)
    train(args.verbose)

    

    