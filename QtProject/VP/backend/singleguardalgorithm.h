#ifndef SINGLEGUARDALGORITHM_H
#define SINGLEGUARDALGORITHM_H

#include <vector>
#include "backend/TiledVS.h"
#include "connectedcomponent.h"
#include "guard.h"

class SingleGuardAlgorithm
{
public:
    SingleGuardAlgorithm();
    void run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    void initializeGuardsUniform(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    void debugInitializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    bool constructF0(tiledMatrix<elev_t>* elev);//Construct the frist frontier (f0)
    //void drawGuardVisibilities(BackendContainer *bc);
    std::vector<std::vector<ConnectedComponent *>> pFrontier; // The boundary of the algorithm until iteration i
    std::vector<Guard> guards;
    float gR = (1.0f + std::sqrt(5.0f)) / 2.0f;
    std::pair<float,float> fibonacciLattice(uint32_t i, uint32_t n);
};

#endif // SINGLEGUARDALGORITHM_H
