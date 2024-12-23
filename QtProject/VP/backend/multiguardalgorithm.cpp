#include "backend/multiguardalgorithm.h"
#include "backend/singleguardalgorithm.h"

MultiGuardAlgorithm::MultiGuardAlgorithm() {}

void MultiGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder){
    std::vector<Guard> rawGuards=SingleGuardAlgorithm::initializeGuards(numGuards,height,radius,elev,initGuardType);
    guards=mixGuardsToOrder(&rawGuards,pairingOrder);
    //debugInitializeGuards(numGuards,height,elev);
    bool isEndAchieved=SingleGuardAlgorithm::constructF0(&guards,&pFrontier,elev);
    if(pFrontier.size()==0){
        cout<<"No solution exists! There is no guard who can see north."<<endl;
        return;
    }
    std::vector<ConnectedComponent*> returningPath;
    if(isEndAchieved==false){
        bool successToAddPremiter=true;
        int prevFrontierIndex=0;
        while(successToAddPremiter==true && isEndAchieved==false)
        {
            successToAddPremiter=false;
            std::vector<ConnectedComponent *> constructingFrontier;//Currently constructing frontier
            for(int g=0;g<guards.size();g++)
            {
                Guard *guard = &(guards.at(g));
                for(int c=0;c<guard->components.size();c++)
                {
                    ConnectedComponent *gConComp=&(guard->components.at(c));
                    if(gConComp->isComponentUsedForFrontier==false)
                    {
                        for(int of=prevFrontierIndex;of>=0;of--)//*** Index for other frontiers (potentially redundant because we only need to check with last frontier)
                        {
                            for(int cp=0;cp<pFrontier.at(of).size();cp++)//Connected component index from previous frontier
                            {
                                ConnectedComponent *ofConComp=pFrontier.at(of).at(cp);//Connected component from other frontier
                                if(ConnectedComponent::checkComponentsIntersection(gConComp,ofConComp))
                                {
                                    gConComp->intersectingCC.push_back(ofConComp);
                                    //ofConComp->intersectingCC.push_back(gConComp);//Only backward path is needed, this is redundant
                                    constructingFrontier.push_back(gConComp);
                                    gConComp->isComponentUsedForFrontier=true;//Block this connected component from being added later
                                    successToAddPremiter=true;
                                    //cout<<gConComp->maxX<<endl;
                                    if(gConComp->maxX==nrows-1)
                                    {//Check if south can be seen
                                        isEndAchieved=true;
                                        returningPath.push_back(gConComp);
                                    }
                                    break;
                                }
                            }
                            if(successToAddPremiter==true){
                                break;
                            }
                        }
                    }
                }
            }
            if(successToAddPremiter==true)
            {
                pFrontier.push_back(constructingFrontier);
                prevFrontierIndex=prevFrontierIndex+1;
            }
        }
        if(returningPath.size()==0){
            cout<<"No solution exists! There is no path from north to south."<<endl;
            return;
        }
        while(!(returningPath.back()->intersectingCC.empty())){
            returningPath.push_back(returningPath.back()->intersectingCC.at(0));
        }
        for(int f=0;f<returningPath.size();f++){
            cout << "Frontier: " << f << endl;
            cout << "   Guard: " << returningPath.at(f)->owner->index << endl;
        }
        for(int f=0;f<pFrontier.size();f++){
            cout << "Frontier: " << f << endl;
            std::unordered_set<int> guardsIndexSet;
            for(int c=0;c<pFrontier.at(f).size();c++){
                guardsIndexSet.insert(pFrontier.at(f).at(c)->owner->index);
            }
            cout << "   Guards: " << endl;
            unordered_set<int>::iterator itr;
            for (itr = guardsIndexSet.begin(); itr != guardsIndexSet.end();itr++)
                cout << (*itr) << endl;
        }
        cout<<"End of multi Guard frontier algorithm"<<endl;
    }
}

std::vector<Guard> MultiGuardAlgorithm::mixGuardsToOrder(std::vector<Guard> *input,int pairingOrder){
    std::vector<Guard> localGuards;
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
        for (int i = 0; i < n; ++i) {
            if (v[i]) {
                g->x=input->at(i).x;
                g->z=input->at(i).z;
                g->h=input->at(i).h;
                g->r=input->at(i).r;
                for(int c = 0; c < input->at(i).components.size(); c++){
                    ConnectedComponent current=input->at(i).components.at(c);
                    bool intersecWithPrevious=false;
                    for(int prevC=0;prevC<g->components.size();prevC++){
                        ConnectedComponent prev=g->components.at(prevC);
                        if(ConnectedComponent::checkComponentsIntersection(&prev,&current)==true){
                            ConnectedComponent *merged=ConnectedComponent::connectTwoComponents(&prev,&current);
                            g->components.erase(g->components.begin()+prevC);
                            merged->owner=g;
                            g->components.insert(g->components.begin()+prevC,*merged);
                            //g->components.push_back(*merged);
                            //prevC=prevC-1;
                            intersecWithPrevious=true;
                        }
                    }
                    if(intersecWithPrevious==false){
                        input->at(i).components.at(c).owner=g;
                        g->components.push_back(input->at(i).components.at(c));
                    }
                }
                cout << (i + 1) << " ";
            }
        }
        localGuards.push_back(*g);
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
    return localGuards;
}
