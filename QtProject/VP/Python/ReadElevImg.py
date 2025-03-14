import argparse
import numpy as np
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

    # Show the plot
    plt.show()

# ---------------------------------
# Read a png file that contains elevation in the red channel
# ---------------------------------
def read_png(filename, verbose=False):
    image = Image.open(filename)
    array = np.array(image)

    ncols, nrows, ncolors = array.shape

    red_channel = array[:, :, 0]  # Red channel is the elevation

    if verbose:
       show_terrain(nrows, ncols, red_channel)

    return red_channel

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read Elevation Image')
    parser.add_argument('INPUT', type=str, help="test.png")    
    parser.add_argument('--verbose', action='store_true', help="verbose")
    args = parser.parse_args()
   
    read_png(args.INPUT, args.verbose)
