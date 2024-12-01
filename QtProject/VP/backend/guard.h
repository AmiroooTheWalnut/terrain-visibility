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
    std::vector<ConnectedComponent> components;
    void findConnected(void);
    void floodFillCC(uint16_t i, uint16_t j);
    void setConnectedComponent(vector<vector<unsigned char>> *pVisited);


    vector<vector<unsigned char>> *pVisited;
    //tiledMatrix<unsigned char>* pVisited=NULL;
    //tiledMatrix<unsigned char>* pGrid=NULL;
    //int row_num;
    //int col_num;

};

#endif // GUARD_H
