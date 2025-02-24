#ifndef MULTIGUARDALGORITHM_H
#define MULTIGUARDALGORITHM_H

#include <vector>
#include "backend/TiledVS.h"
#include "connectedcomponent.h"
#include "singleguardalgorithm.h"
#include "guard.h"

class MultiGuardAlgorithm : public SingleGuardAlgorithm
{
public:
    MultiGuardAlgorithm();
    void mixGuardsToOrder(int pairingOrder);
    bool run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder);// PairingOrder refers to the order of considering guards together.                                                                                                                            // For instance two guards at a time or three and so on.
    virtual void exportForILP(std::string filename = "ilpSingle.txt");
    inline std::vector<Guard *> *getGuards(void) { return SingleGuardAlgorithm::getGuards(); }
    inline std::vector<std::vector<ConnectedComponent *>> *getFrontier(void) { return SingleGuardAlgorithm::getFrontier(); }
};


#endif // MULTIGUARDALGORITHM_H
