# Read guard file input
# Input format:
#     Guard K                 <for each guard>
#     ConnectedComponent N    <at least one line>
#     Intersecting I          <at least zero line>
#     ....
#     CrossNorth A            <at least one line>
#     CrossSouth B            <at least one line>
#

class classComp:
    def __init__(self, id, parentID):
        self.id = id
        self.parentID = parentID
        self.intersects = []

    def addIntersect(self, id):
        self.intersects.append(id)

    # For Geogebra export
    def setLocation(self, cx, cy, radius):
        self.cx = cx
        self.cy = cy
        self.radius = radius

class classGuard:
    def __init__(self, id):
        self.id = id
        self.comps = []

    def addComp(self, comp):
        self.comps.append(comp)

def readInput(f, verbose):
    gGuards = []   # Contains the comps
    gComps = []    # Contains the comps
    gNorths = []   # Contains IDs only
    gSouths = []   # Contains IDs only

    guardnum = -1
    compnum = -1
 
    # Read input file and build the connectedness map
    for l in f.readlines():
        typeStr, numStr = l.split()
        num = int(numStr)

        if typeStr == "Guard":
            guardnum = num
            guard = classGuard(guardnum)
            gGuards.append(guard)
        elif typeStr == "ConnectedComponent":
            compnum = num
            comp = classComp(compnum, guardnum)
            gGuards[guardnum].addComp(comp)
            gComps.append(comp)
        elif typeStr == "Intersecting":
            gComps[compnum].addIntersect(num)
        elif typeStr == "CrossNorth":
            gNorths.append(num)
        elif typeStr == "CrossSouth":
            gSouths.append(num)
        else:
            raise Exception("Uncognized type!")

    if len(gNorths) == 0 or len(gSouths) == 0:
        print("There is no north-crossing or no south-crossing connected components!")
        return

    if verbose:
        print("----------Guard/Region Info----------")
        print("nGuard = " + str(len(gGuards)))
        print("gGuards:")
        for i in range(len(gGuards)):
            guard = gGuards[i]
            for j in range(len(guard.comps)):
                comp = guard.comps[j]
                print(f"{i} = {comp.id}")
        print("gComps:")
        print(gComps)
        print("Intersections:")
        for i in range(len(gComps)):
            for j in range(len(gComps)):
                if j in gComps[i].intersects:
                    print(f"Connected: {i}, {j}")
        print("gNorths:")
        print(gNorths)
        print("gSouths:")
        print(gSouths)

    return gGuards, gComps, gNorths, gSouths
