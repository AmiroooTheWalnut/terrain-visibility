#include "backend/multiguardalgorithm.h"
#include "backend/singleguardalgorithm.h"

MultiGuardAlgorithm::MultiGuardAlgorithm() {}

bool MultiGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder)
{
    bool retVal = true;

    Print_Time((char*)"MultiGuardAlgorithm::run start");

    mixGuardsToOrder(pairingOrder);

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

    Print_Time((char*)"MultiGuardAlgorithm::run end");

    return retVal;
}

void MultiGuardAlgorithm::mixGuardsToOrder(int pairingOrder)
{
    std::vector<Guard *> localGuards;

    int newIndexCounter=0;
    int paired = 0;

    do
    {
        Guard *ng=new Guard();
        ng->index=newIndexCounter;

        for(std::vector<Guard *>::iterator iter = guards.begin(); iter != guards.end(); iter++)
        {   // Should randomize the order of the guards!
            Guard *gg = *iter;

            ng->x = gg->x;
            ng->z = gg->z;
            ng->h = gg->h;
            ng->r = gg->r;

            // Merge all the components from the ith guard into the current guard
            // Combine the components if there is intersection
            for (std::vector<ConnectedComponent *>::iterator it = gg->components.begin(); it != gg->components.end(); ++it)
            {
                ConnectedComponent *current = *it;
                bool intersecWithPrevious=false;

                for (std::vector<ConnectedComponent *>::iterator it2 = ng->components.begin(); it2 != ng->components.end(); ++it2)
                {
                    ConnectedComponent *prev = *it2;
                    if(ConnectedComponent::checkComponentsIntersection(prev, current)==true)
                    {
                        ConnectedComponent *merged=ConnectedComponent::connectTwoComponents(prev, current);
                        ng->components.erase(it2);
                        merged->owner=ng;
                        ng->components.insert(it2, merged);
                        intersecWithPrevious=true;
                    }
                }
                if(intersecWithPrevious==false)
                {
                    current->owner=ng;
                    ng->components.push_back(current);
                }
            }
            // Remove the guard from the list since it has been merged into ng
            guards.erase(iter);
            cout << "Guard size = " << guards.size() << endl;
            paired++;
            if (paired == pairingOrder)
            {
                paired = 0;
                break;
            }
            if (guards.size() == 0)
            {
                break;
            }
        }
        localGuards.push_back(ng);
        newIndexCounter=newIndexCounter+1;
        // Need to not merge guards that have already been merged
    } while (guards.size() > 0);

    guards = localGuards;
}
