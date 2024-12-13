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
    void run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType);
    static std::vector<Guard> initializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType);
    static std::vector<Guard> initializeGuardsFib(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    static std::vector<Guard> initializeGuardsSquareUniform(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    void debugInitializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    static bool constructF0(std::vector<Guard> *guards, std::vector<std::vector<ConnectedComponent *>> *pFrontier,tiledMatrix<elev_t>* elev);//Construct the frist frontier (f0)
    std::vector<std::vector<ConnectedComponent *>> pFrontier; // The boundary of the algorithm until iteration i
    std::vector<Guard> guards;
    static inline float gR = (1.0f + std::sqrt(5.0f)) / 2.0f;
    static std::pair<float,float> fibonacciLattice(uint32_t i, uint32_t n);
};

#endif // SINGLEGUARDALGORITHM_H
