#ifndef GUARD_H
#define GUARD_H

#include <vector>
#include <cstdint>
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
    std::vector<ConnectedComponent *> components; // Use pointers to make sure of persistent memory and prevent copy
    void findConnected(void);
    void floodFill(uint16_t sr, uint16_t sc);
    void setConnectedComponent(void);

    void resetUsedForFrontier(void);
    void clear(void);
};

#endif // GUARD_H
