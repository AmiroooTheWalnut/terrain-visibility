#ifndef MULTIGUARDALGORITHM_H
#define MULTIGUARDALGORITHM_H

#include <vector>
#include "backend/TiledVS.h"
#include "connectedcomponent.h"
#include "guard.h"

class MultiGuardAlgorithm
{
public:
    MultiGuardAlgorithm();
    static std::vector<Guard> mixGuardsToOrder(std::vector<Guard> *input,int pairingOrder);
    void run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder);// PairingOrder refers to the order of considering guards together.
                                                                                                                            // For instance two guards at a time or three and so on.
    std::vector<std::vector<ConnectedComponent *>> pFrontier; // The boundary of the algorithm until iteration i
    std::vector<Guard> guards;
};

#endif // MULTIGUARDALGORITHM_H
