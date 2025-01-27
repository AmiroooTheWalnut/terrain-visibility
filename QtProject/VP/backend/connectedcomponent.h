#ifndef CONNECTEDCOMPONENT_H
#define CONNECTEDCOMPONENT_H

#include <vector>
#include <bits/stdc++.h>
#include <string>
#include "guard.h"


/* Not sure if this is a efficient data structure */
struct ConnectedRow
{
    int compRow;
    std::vector<int> xStart;
    std::vector<int> xEnd;
};

class ConnectedComponent
{
public:
    Guard *owner;
    ConnectedComponent();
    static ConnectedComponent* connectTwoComponents(ConnectedComponent *a, ConnectedComponent *b);
    static ConnectedComponent* setConnectedComponent(std::vector<std::vector<bool>> bitmap);
    static bool checkComponentsIntersection(ConnectedComponent *a, ConnectedComponent *b);
    static int binarySearchIndex(ConnectedComponent *in, int rowIndex);
    std::vector<ConnectedRow> colRangeInRow;
    int maxX;
    int minX;
    int maxZ;
    int minZ;
    bool isComponentUsedForFrontier=false;
    std::vector<ConnectedComponent*> intersectingCC;
    inline void resetUsedForFrontier(void) { isComponentUsedForFrontier = false; }
};

#endif // CONNECTEDCOMPONENT_H
