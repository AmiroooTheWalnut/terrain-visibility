#ifndef CONNECTEDCOMPONENT_H
#define CONNECTEDCOMPONENT_H

#include <vector>
#include <bits/stdc++.h>
#include <string>

class ConnectedComponent
{
public:
    ConnectedComponent();
    std::string name;
    ConnectedComponent connectTwoComponents(ConnectedComponent a, ConnectedComponent b);
    bool checkComponentsIntersection(ConnectedComponent a, ConnectedComponent b);
    std::vector<std::pair<int,int>> colRangeInRow;
};

#endif // CONNECTEDCOMPONENT_H
