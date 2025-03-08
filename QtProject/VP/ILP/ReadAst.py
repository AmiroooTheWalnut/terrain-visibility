import argparse
import re
import math
from TerrainInput import classComp, classGuard, readInput

# Parse straight line in the form y = b
def parse_asymptote_lines(asymptote_code):
    lines = []

    # Regular expression to capture the y-intercepts
#    matches = re.findall(r'0\*xmin\s*[\+\-]\s*([\d\.]+)', asymptote_code)
    matches = re.findall(r'0\*xmin\s*([+-]\s*\d+\.?\d*)', asymptote_code)
    matches = [m.replace(" ", "") for m in matches]

    # Convert to float
    y_intercepts = [float(match) for match in matches]

    for y in y_intercepts:
       lines.append({
           "y": y
       })

    return lines

# Parse circle
def parse_asymptote_circles(asymptote_code):
    # Regular expression to match the circle drawing commands, including the color part (e.g., + red)
    circle_pattern = re.compile(r'draw\(circle\(\(([-\d.]+),([-\d.]+)\), ([-\d.]+)\), linewidth\(\d+\)(?: \+ (\w+))?\);')

    # Find all the circle data
    circles = []
    for match in circle_pattern.findall(asymptote_code):
        x, y, radius, color = match
        circles.append({
            "center_x": float(x),
            "center_y": float(y),
            "radius": float(radius),
            "color": color if color else "default"
        })

    return circles

# Check if two disks intersect
def disk_intersect(cx1, cy1, rad1, cx2, cy2, rad2):
    distance = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)
    return (distance < rad1 + rad2)

# Check if disk intersect with a line y = b
def line_intersect(cy, rad, b):
    return (b >= cy - rad and b <= cy + rad)

# Main loop
def run(file_path, verbose):
    # Example usage
    with open(file_path, "r") as f:
        asymptote_code = f.read()
        circles = parse_asymptote_circles(asymptote_code)
        lines = parse_asymptote_lines(asymptote_code)

    # Build connected graph and output file
    gGuards = []   # Contains the comps
    gComps = []    # Contains the comps
    gNorths = []   # Contains IDs only
    gSouths = []   # Contains IDs only

    currentColor = ""
    guard = None
    # Identify the guards and their components
    for i, circle in enumerate(circles, start=0):
        if verbose:
            print(f"Circle {i}: {circle['center_x']:.4g}, {circle['center_y']:.4g}, {circle['radius']:.4g}, {circle['color']}")

        if circle['color'] != currentColor:
            guard = classGuard(len(gGuards))
            gGuards.append(guard)
            currentColor = circle['color']
        assert guard != None, "Guard is none!"
        comp = classComp(len(gComps), guard.id)
        guard.addComp(comp)
        gComps.append(comp)
        comp.setLocation(circle['center_x'], circle['center_y'], circle['radius'])

    # Figure out the intersecting components
    for comp1 in gComps:
        for comp2 in gComps:
            if comp1.id != comp2.id and comp2.id not in comp1.intersects:
                if (disk_intersect(comp1.cx, comp1.cy, comp1.radius, comp2.cx, comp2.cy, comp2.radius)):
                    comp1.addIntersect(comp2.id)

    # Figure out which components intersect North and South
    for i, line in enumerate(lines, start=0):
        assert i < 2, "There should only be North and South lines!"
        if verbose:
            print(f"Line {i}: y = {line['y']:.4g}")
        for comp in gComps:
            if line_intersect(comp.cy, comp.radius, line['y']):
                if i==0:
                    gNorths.append(comp.id)
                if i==1:
                    gSouths.append(comp.id)

    # -------------Guards and Components below:-------------
    for guard in gGuards:
        print(f"Guard {guard.id}")
        for comp in guard.comps:
            print(f"ConnectedComponent {comp.id}")
            for id in comp.intersects:
                print(f"Intersecting {id}")

    for id in gNorths:
        print(f"CrossNorth {id}")
    for id in gSouths:
        print(f"CrossSouth {id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ReadSVG')
    parser.add_argument('INPUT', type=str, help="test.txt")
    parser.add_argument('--verbose', action='store_true', help="-v")
    args = parser.parse_args()
   
    run(args.INPUT, args.verbose)
