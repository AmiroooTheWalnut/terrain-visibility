#ifndef GUARD_H
#define GUARD_H

#include <vector>
#include "TiledVS.h"

class ConnectedComponent;

class Guard
{
public:
    explicit Guard();
    int x;
    int h;
    int z;
    int r;
    int index;
    std::vector<ConnectedComponent> perimeter;
    void findConnected(void);
    void floodFillCC(int i, int j);
    void setConnectedComponent(void);
};

#endif // GUARD_H
