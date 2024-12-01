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
    // std::string name; -- Q to Amir: Why is name here?
    static ConnectedComponent connectTwoComponents(ConnectedComponent *a, ConnectedComponent *b);
    static bool checkComponentsIntersection(ConnectedComponent *a, ConnectedComponent *b);
    static int binarySearchIndex(ConnectedComponent *in, int rowIndex);
    std::vector<ConnectedRow> colRangeInRow;
    int maxX;
    int minX;
    int maxZ;
    int minZ;
    bool isComponentUsedForFrontier=false;
};

#endif // CONNECTEDCOMPONENT_H
