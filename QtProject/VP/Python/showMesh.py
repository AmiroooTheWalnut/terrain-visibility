import pyvista as pv
import numpy as np
from ReadElevImg import read_png
import argparse
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import numpy as np
import pyvista as pv

def meshVisibility(mesh, points, radius, sky_height, num_rays=8):
    visibilities = []

    for point in points:
        visible = 0
        base_height = point[2]  # elevation

        # Cast rays in a circle around Z-axis
        for angle in np.linspace(0, 2*np.pi, num_rays, endpoint=False):
            dx = np.cos(angle)
            dy = np.sin(angle)

            # Compute max dz to not exceed sky_height
            horizontal_dist = radius
            max_dz = min(sky_height, sky_height + base_height) # Ensure no overshoot
            dz = max_dz / np.sqrt(1 + dx**2 + dy**2)

            direction = np.array([dx, dy, dz])
            direction /= np.linalg.norm(direction)

            # Define a long ray to simulate the sky at constant height
            origin = point + 1e-3 * direction  # avoid self-hit
            target = origin + radius * direction

            # Clamp target Z to not exceed sky_height
            if target[2] > base_height + sky_height:
                target[2] = base_height + sky_height

            # Perform ray tracing
            _, intersect_ids = mesh.ray_trace(origin, target, first_point=True)
            if len(intersect_ids) == 0:
                visible += 1  # no hit means ray reached sky

        visibilities.append(visible / num_rays)

    return np.array(visibilities)

def triangulate(ncols, nrows, elev):
    x = np.linspace(0, ncols-1, int(ncols/20))
    y = np.linspace(0, nrows-1, int(nrows/20))
    xx, yy = np.meshgrid(x, y)

    # Ensure the shapes match
    xx = xx.flatten()
    yy = yy.flatten()
    zz = elev[yy.astype(int), xx.astype(int)]

    # Stack coordinates into a single array of shape (n_points, 3)
    points = np.column_stack((xx, yy, zz))

    # Create a PyVista PolyData object
    terrain = pv.PolyData(points)

    # Triangulate the points using Delaunay triangulation
    triangulated_terrain = terrain.delaunay_2d()

    # Plot the triangulated terrain
    #triangulated_terrain.plot(show_edges=True)
    plotter = pv.Plotter()
    plotter.add_mesh(triangulated_terrain, show_edges=True)
    plotter.show()

    return triangulated_terrain, points

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Triangulation')
    parser.add_argument('INPUT', type=str, help="test.png")
    args = parser.parse_args()

    image = Image.open(args.INPUT)
    array = np.array(image)
    ncols, nrows, ncolors = array.shape
    red_channel = array[:, :, 0]  # Red channel is the elevation

    print("Showing triangulation mesh")
    trangulated_terrain, points = triangulate(ncols, nrows, red_channel)

    # Calculate visibility to the sky from points on the terrain
    # 3D geometric ray-mesh intersection problem
    #visibility_values = meshVisibility(mesh, points, radius=120.0, sky_height=500.0)

    print("Completed")
