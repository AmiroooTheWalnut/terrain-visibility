#include "backend/multiguardalgorithm.h"
#include "backend/singleguardalgorithm.h"

MultiGuardAlgorithm::MultiGuardAlgorithm() {}

bool MultiGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder)
{
    bool retVal = true;

    Print_Time((char*)"MultiGuardAlgorithm::run start");

    SingleGuardAlgorithm::initializeGuards(numGuards,height,radius,elev,initGuardType);

    mixGuardsToOrder(pairingOrder);

    // Pairing Order shouldn't matter!!! Remove it?

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
    std::vector<Guard *> *input = &guards;
    int n=input->size();

    // int guardIndices[n];
    // for(int i=0;i<n;i++){
    //     guardIndices[i]=i;
    // }

    std::vector<bool> v(n);
    std::fill(v.end() - pairingOrder, v.end(), true);
    int newIndexCounter=0;
    do {
        Guard *g=new Guard();
        g->index=newIndexCounter;
        for (int i = 0; i < n; ++i)
        {
            if (v[i])
            {
                Guard *gg = input->at(i);
                g->x = gg->x;
                g->z = gg->z;
                g->h = gg->h;
                g->r = gg->r;
                for (std::vector<ConnectedComponent *>::iterator it = gg->components.begin(); it != gg->components.end(); ++it)
                {
                    ConnectedComponent *current = *it;
                    bool intersecWithPrevious=false;

                    for (std::vector<ConnectedComponent *>::iterator it2 = g->components.begin(); it2 != g->components.end(); ++it2)
                    {
                        ConnectedComponent *prev = *it2;
                        if(ConnectedComponent::checkComponentsIntersection(prev, current)==true)
                        {
                            ConnectedComponent *merged=ConnectedComponent::connectTwoComponents(prev, current);
                            g->components.erase(it2);
                            merged->owner=g;
                            g->components.insert(it2, merged);
                            intersecWithPrevious=true;
                        }
                    }
                    if(intersecWithPrevious==false)
                    {
                        current->owner=g;
                        g->components.push_back(current);
                    }
                }
                cout << (i + 1) << " ";
            }
        }
        localGuards.push_back(g);
        newIndexCounter=newIndexCounter+1;
        cout << endl;
    } while (std::next_permutation(v.begin(), v.end()));


    // sort(guardIndices, guardIndices + n);
    // int newIndexCounter=0;
    // do {
    //     Guard *g=new Guard();
    //     g->x=input[guardIndices[0]].x;
    //     g->z=input[guardIndices[0]].z;
    //     g->h=input[guardIndices[0]].h;
    //     g->r=input[guardIndices[0]].r;
    //     g->index=newIndexCounter;
    //     for(int i = 0; i < n; i++){
    //         for(int c = 0; c < input[guardIndices[0]].components.size(); c++){
    //             g->components.push_back(input[guardIndices[0]].components[c]);
    //         }
    //         cout << guardIndices[i] << " ";
    //     }
    //     localGuards.push_back(*g);
    //     newIndexCounter=newIndexCounter+1;
    //     cout << endl;
    // } while (next_permutation(guardIndices, guardIndices + n));

    // Replace the guard vector with this new vector
    guards = localGuards;
}
