#ifndef CONNECTEDCOMPONENT_H
#define CONNECTEDCOMPONENT_H

#include <vector>
#include <bits/stdc++.h>
#include <string>


/* Not sure if this is a efficient data structure */
struct ConnectedRow
{
    int compRow;
    int xStart;
    int xEnd;
};

class ConnectedComponent
{
public:
    ConnectedComponent();
    // std::string name; -- Q to Amir: Why is name here?
    ConnectedComponent connectTwoComponents(ConnectedComponent a, ConnectedComponent b);
    bool checkComponentsIntersection(ConnectedComponent a, ConnectedComponent b);
    std::vector<ConnectedRow> colRangeInRow;
};

#endif // CONNECTEDCOMPONENT_H
