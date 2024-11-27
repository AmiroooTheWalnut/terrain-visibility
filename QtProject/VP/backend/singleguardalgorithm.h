#ifndef SINGLEGUARDALGORITHM_H
#define SINGLEGUARDALGORITHM_H

#include <vector>
#include <iostream>
#include <algorithm>
#include "backend/TiledVS.h"
#include "connectedcomponent.h"
#include "guard.h"

class SingleGuardAlgorithm
{
public:
    SingleGuardAlgorithm();
    void run(int numGuards, int height, tiledMatrix<elev_t>* elev);
    void initializeGuardsUniform(int numGuards, int height, tiledMatrix<elev_t>* elev);
    //void drawGuardVisibilities(BackendContainer *bc);
    std::vector<ConnectedComponent *> pPerimeter; // Actually owned by the guards
    std::vector<Guard> guards;
};

#endif // SINGLEGUARDALGORITHM_H
