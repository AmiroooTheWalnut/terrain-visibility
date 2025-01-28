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
    virtual void run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder=0);
    virtual inline std::vector<Guard *> *getGuards(void) { return &guards; }
    virtual inline std::vector<std::vector<ConnectedComponent *>> *getFrontier(void) { return &frontier; }

    // std::vector of Guard pointer to avoid copying guard elements each time
    void initializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType);
    void initializeGuardsFib(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    void initializeGuardsSquareUniform(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    void debugInitializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev);
    bool constructF0(tiledMatrix<elev_t>* elev);//Construct the firstt frontier (f0)

    static inline float gR = (1.0f + std::sqrt(5.0f)) / 2.0f;
    std::pair<float,float> fibonacciLattice(uint32_t i, uint32_t n);
    void clearAll(void);

protected:
    std::vector<Guard *> guards;
    std::vector<std::vector<ConnectedComponent *>> frontier; // The boundary of the algorithm until iteration i
};


#endif // SINGLEGUARDALGORITHM_H
