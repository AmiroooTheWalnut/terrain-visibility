import argparse
import numpy as np
import os
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# ---------------------------------
# Show terrain in 3D
# Elevation is in the 2D array (value range 0-255)
# ---------------------------------
def show_terrain(width, height, array):
        
    x = np.linspace(0, width-1, width)
    y = np.linspace(0, height-1, height)
    x, y = np.meshgrid(x, y)

    # Create a 3D plot
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the array as the Z axis
    ax.plot_surface(x, y, array)
    ax.set_zlim(0, 500)
    ax.view_init(elev=30, azim=225)  # Rotate view to focus on (0,0,0)


    # Set labels for the axes
    ax.set_xlabel('X (Width)')
    ax.set_ylabel('Y (Height)')
    ax.set_zlabel('Elevation')

    ax.text(x=400, y=400, z=400, s="Original Terrain", color='black', fontsize=12)

    # Show the plot
    plt.show()

# ---------------------------------
# Read a png file that contains elevation in the red channel
# ---------------------------------
def read_png(filename, verbose=False, enableShow=False):
    image = Image.open(filename)
    array = np.array(image)

    ncols, nrows, ncolors = array.shape

    red_channel = array[:, :, 0]  # Red channel is the elevation

    if enableShow:
       show_terrain(ncols, nrows, red_channel)

    return red_channel

# ---------------------------------
# Read a hgt file
# ---------------------------------
def read_hgt(filename, verbose=False, enableShow=False):

    ncols = 1201
    nrows = 1201

    elev = np.fromfile(filename, np.dtype('>i2'), ncols*nrows).reshape((ncols, nrows))

    if enableShow:
        show_terrain(ncols, nrows, elev)

    return elev

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read Elevation Image')
    parser.add_argument('INPUT', type=str, help="test.png")    
    parser.add_argument('--verbose', action='store_true', help="verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing terrain")
    args = parser.parse_args()

    filename = args.INPUT
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    ext = os.path.splitext(filename)[1]
    if ext == ".png":
        read_png(filename, verbose, enableShow)
    elif ext == ".hgt":
        read_hgt(filename, verbose, enableShow)
    else:
        print(f"Unrecognized extension: {ext}")
