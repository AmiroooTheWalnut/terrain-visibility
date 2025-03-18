import numpy as np
import time

# ---------------------------------
# Calculate visibility of a guard 
# Elevation is in array elev
# Output is a viewshed
# See Franklin's viewshed algorithm
# ---------------------------------
def calc_vis(guard, elev, verbose):
    if verbose:
        start_time = time.time()

    nrows, ncols = elev.shape
    viewshed = np.zeros((nrows, ncols), dtype=int)

    obs = np.array((guard.x, guard.y), dtype=int)
    radius = guard.r
    xmin = max(obs[0] - radius, -10)
    ymin = max(obs[1] - radius, -10)
    xmax = min(obs[0] + radius, nrows + 9)
    ymax = min(obs[1] + radius, ncols + 9) 
    xwidth = xmax - xmin
    ywidth = ymax - ymin
    perimeter = 2 * (xwidth + ywidth)    
  
    viewshed[obs[0]][obs[1]] = 1 # Observer is visible from itself

    # Observer distance about sea level, incl distance above ground.
    obsAltitude = float(elev[obs[0]][obs[1]]) + float(guard.h)

    # The target is in turn every point along the smaller of the border or a box
    # of side 2*radius around the observer.

    # xmax etc are coords of pixels, not of the edges between the pixels.  I.e.,
    # xmin=5, xmax=7 means 3 pixels.
    # A 3x3 regions has a perimeter of 9.
    if xmin == xmax or ymin == ymax:
        return viewshed

    tgt = np.zeros(2, dtype=int)
    for ip in range(perimeter):
        #define cells on square perimeter
        if ip < ywidth:
            tgt[0] = xmax
            tgt[1] = ymax - ip
        elif ip < xwidth + ywidth:
            tgt[0] = xmax - (ip - ywidth)
            tgt[1] = ymin
        elif ip < 2 * ywidth + xwidth:
            tgt[0] = xmin
            tgt[1] = ymin + (ip - xwidth - ywidth)
        else:
            tgt[0] = xmin + (ip - 2 * ywidth - xwidth)
            tgt[1] = ymax

        # This occurs only when observer is on the edge of the region
        if obs[0] == tgt[0] and obs[1] == tgt[1]:
            continue

        # Run a line of sight out from obs to target
        delta = np.array((tgt[0] - obs[0], tgt[1] - obs[1]), dtype=int)
        inciny = int(abs(delta[0]) < abs(delta[1]))

        # Step along the coord (X or Y) that varies the most from the observer to
        # the target.  Inciny says which coord that is.  Slope is how fast the
        # other coord varies.
        slope = float(delta[1 - inciny]) / float(delta[inciny])

        if delta[inciny] > 0:
            sig = 1
        else:
            sig = -1
        horizon_slope = -99999     # Slope (in vertical plane) to horizon so far.

	# i=0 would be the observer, which is always visible
        p = np.array((0, 0), dtype=int)
        i = sig
        while i != delta[inciny]:
            p[inciny] = obs[inciny] + i
            p[1 - inciny] = obs[1 - inciny] + int(i * slope)

            # Have we reached the edge of the area?
            if p[0] < 0 or p[0] >= nrows or p[1] < 0 or p[1] >= ncols:
                break

            # A little optimization, so we don't need to use long long every time (int is faster)
            valX = abs(p[0] - obs[0])
            valY = abs(p[1] - obs[1])
            if valX + valY > radius:
                # but sometimes we still need to use them...
                if valX * valX + valY * valY > radius * radius:
                    break

            pelev = float(elev[p[0]][p[1]])

            # Slope from the observer, incl the observer_ht, to this point, at ground
            # level.  The slope is projected into the plane XZ or YZ, depending on
            # whether X or Y is varying faster, and thus being iterated thru.
            s = (pelev - obsAltitude) / float(abs((p[inciny] - obs[inciny])))

            if horizon_slope < s:
                horizon_slope = s

            horizon_alt = obsAltitude + horizon_slope * abs(p[inciny] - obs[inciny])

            if pelev + float(guard.h) >= horizon_alt:
                viewshed[p[0]][p[1]] = 1

            i += sig

    #debugPrintViewShed(viewshed)

    if verbose:
        print(f"Time to execute Visibility algorithm = {end_time - start_time:.2g} seconds")
	
    return viewshed

# -----------------------------
# Print gCompMask
# -----------------------------
def debugPrintViewShed(viewshed):

    width, height = viewshed.shape
    for i in range(width):
        s = "Row " + str(i) + ": "
        for j in range(height):
            s = s + "," + str(viewshed[i][j])
        print(s)
