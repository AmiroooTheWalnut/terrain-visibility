#include "backend/multiguardalgorithm.h"
#include "backend/singleguardalgorithm.h"

MultiGuardAlgorithm::MultiGuardAlgorithm() {}

bool MultiGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder)
{
    bool retVal = true;

    Print_Time((char*)"MultiGuardAlgorithm::run start");

    // Update numGuards after guards are paired
    numGuards = guards.size();

    //debugInitializeGuards(numGuards,height,elev);
    bool isEndAchieved=SingleGuardAlgorithm::constructF0(elev);
    if(frontier.size()==0)
    {
        cout<<"No solution exists! Failed to construct F0"<<endl;
        retVal = false;
    }

    // It is the same code and should be, so may as well just call it, so we only keep track of a single copy
    if (retVal)
    {
        retVal = SingleGuardAlgorithm::run(numGuards, height, radius, elev, initGuardType);
    }
    cout<<"End of multi Guard frontier algorithm"<<endl;

    Print_Time((char*)"MultiGuardAlgorithm::run end");

    return retVal;
}

/* Per Dr. Efrat, we add guards and connected components by combine every pair of guards */
/* So we ignore argument pairingOrder */
void MultiGuardAlgorithm::mixGuardsToOrder(int pairingOrder)
{
    // Avoid doubling multiple times because each time we got n^2 guards
    if (guardsPaired) return;
    guardsPaired = true;

    // Put all new guards on a separate vector during the loop the original vector is kept constant
    std::vector<Guard *> newGuards;
    int index = guards.size();

    for (std::vector<Guard *>::iterator it1 = guards.begin(); it1 != guards.end(); ++it1)
    {
        Guard *guard1 = *it1;
        for (std::vector<Guard *>::iterator it2 = it1+1; it2 != guards.end(); ++it2)
        {
            Guard *guard2 = *it2;
            if (guard1 != guard2)
            {
                Guard *ng = Guard::unionTwoGuards(guard1, guard2);
                ng->index = index++;
                newGuards.push_back(ng);
            }
        }
    }

    // Now attach newGuards to guards
    guards.insert(guards.end(), newGuards.begin(), newGuards.end());
}

void MultiGuardAlgorithm::exportForILP(std::string filename)
{
    SingleGuardAlgorithm::exportForILP("ilpMultiple.txt");
}

