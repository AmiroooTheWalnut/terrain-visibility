import pyvista as pv
import numpy as np
from ReadElevImg import read_png
import argparse
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import numpy as np
import pyvista as pv

class Quadtree:
    def __init__(self, grid_size, max_depth=6):
        self.grid_size = grid_size
        self.max_depth = max_depth
        self.tree = {}
    
    def subdivide(self, x_start, y_start, size, depth):
        """ Recursively subdivide the grid """
        if depth >= self.max_depth:
            return
        
        # Define the four quadrants
        mid_x = x_start + size // 2
        mid_y = y_start + size // 2
        
        # Recursive subdivision
        self.subdivide(x_start, y_start, size // 2, depth + 1)  # Top-left
        self.subdivide(mid_x, y_start, size // 2, depth + 1)   # Top-right
        self.subdivide(x_start, mid_y, size // 2, depth + 1)   # Bottom-left
        self.subdivide(mid_x, mid_y, size // 2, depth + 1)    # Bottom-right

    def generate_mesh(self, grid, x_start, y_start, size, depth):
        """Generate a terrain mesh for each quadtree subdivision"""
        if depth >= self.max_depth:
            # Create a simple grid (mesh) for the quadrant
            x = np.linspace(x_start, x_start + size, size)
            y = np.linspace(y_start, y_start + size, size)
            xx, yy = np.meshgrid(x, y)
            zz = np.sin(xx ** 2 + yy ** 2)  # Simple terrain function

            # Create a PyVista grid (mesh) for the terrain quadrant
            grid = pv.StructuredGrid(xx, yy, zz)
            return grid
        else:
            return None  # No mesh at this level, since it's a deeper subdivision

    def build(self):
        """ Recursively build the quadtree and generate meshes """
        self.subdivide(0, 0, self.grid_size, 0)
        meshes = []
        for x_start in range(0, self.grid_size, self.grid_size // 2):
            for y_start in range(0, self.grid_size, self.grid_size // 2):
                mesh = self.generate_mesh(None, x_start, y_start, self.grid_size // 2, 0)
                if mesh is not None:
                    meshes.append(mesh)
        return meshes

def showQuadTree(ncols, nrows, elev):

    # Create a quadtree (assume ncols = nrows)
    quadtree = Quadtree(grid_size=ncols)
    meshes = quadtree.build()

    # Combine the meshes into a single PyVista plot
    terrain = pv.Plotter(off_screen=True)
    for mesh in meshes:
        terrain.add_mesh(mesh)

    # Display the terrain with PyVista
    terrain.show(screenshot="quadExample.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('INPUT', type=str, help="test.png")
    args = parser.parse_args()

    image = Image.open(args.INPUT)
    array = np.array(image)
    ncols, nrows, ncolors = array.shape
    red_channel = array[:, :, 0]  # Red channel is the elevation

    pv.OFF_SCREEN = True

    print("Showing quadtree")
    showQuadTree(ncols, nrows, red_channel)
 
    print("Completed")
