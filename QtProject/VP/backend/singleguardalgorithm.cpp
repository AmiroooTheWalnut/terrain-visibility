#include <iostream>
#include <unordered_set>
#include "singleguardalgorithm.h"

SingleGuardAlgorithm::SingleGuardAlgorithm() {

}

void SingleGuardAlgorithm::run(int numGuards, int height, tiledMatrix<elev_t>* elev){
    initializeGuardsUniform(numGuards,height,elev);
    //debugInitializeGuards(numGuards,height,elev);
    bool isEndAchieved=constructF0(elev);
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
                                }
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
            cout << "   Gaurd: " << returningPath.at(f)->owner->index << endl;
        }
        for(int f=0;f<pFrontier.size();f++){
            cout << "Frontier: " << f << endl;
            std::unordered_set<int> gaurdsIndexSet;
            for(int c=0;c<pFrontier.at(f).size();c++){
                gaurdsIndexSet.insert(pFrontier.at(f).at(c)->owner->index);
            }
            cout << "   Guards: " << endl;
            unordered_set<int>::iterator itr;
            for (itr = gaurdsIndexSet.begin(); itr != gaurdsIndexSet.end();itr++)
                cout << (*itr) << endl;
        }

        cout<<"End of single Guard frontier algorithm"<<endl;

    }
}

bool SingleGuardAlgorithm::constructF0(tiledMatrix<elev_t>* elev){
    //Initialize all connected components (isComponentUsedForFrontier variable to false)
    for(int g=0;g<guards.size();g++){
        Guard *guard = &guards.at(g);
        for(int c=0;c<guards.at(g).components.size();c++){
            guard->components.at(c).isComponentUsedForFrontier=false;
        }
    }
    bool isEndFound=false;//Checks if the algorithm should finish with a single guard that sees north to south
    std::vector<ConnectedComponent *> f0;
    for(int g=0;g<guards.size();g++){
        Guard *guard = &guards.at(g);
        for(int c=0;c<guards.at(g).components.size();c++){
            if(guards.at(g).components.at(c).minX==0){//Guard can see north with connected component "c"
                if(guards.at(g).components.at(c).maxX==elev->nrows-1){//Guard can see the end (south)
                    isEndFound=true;
                }
                f0.push_back(&(guards.at(g).components.at(c)));
                guards.at(g).components.at(c).isComponentUsedForFrontier=true;//Make sure this connected component won't be used for later frontiers
            }
        }
    }
    pFrontier.push_back(f0);
    return isEndFound;//Return boolean indicating if a single guard is enough
}

void SingleGuardAlgorithm::initializeGuardsUniform(int numGuards, int height, tiledMatrix<elev_t>* elev){
    float nGRows=std::max(1.0,std::sqrt((numGuards)*(nrows/ncols)));
    float nGCols=std::max(1.0,std::sqrt((numGuards)*(ncols/nrows)));

    float nRowGuardPixels=std::floor(std::max(1.0f,((float)ncols/(float)(nGCols+1))));
    float nColGuardsPixels=std::floor(std::max(1.0f,((float)nrows/(float)(nGRows+1))));

    //int maxXSeenDebug=0;

    int counter=0;
    for(int i=1;i<=nGRows;i++){
        for(int j=1;j<=nGCols;j++){
            Guard *g=new Guard();
            g->x=i*nRowGuardPixels;
            g->z=j*nColGuardsPixels;
            g->h=50;
            g->r=1200;
            g->index=counter;
            g->findConnected();
            guards.push_back(*g);
            counter=counter+1;
            // for(int m=0;m<g.components.size();m++){
            //     if(maxXSeenDebug<g.components.at(m).maxX){
            //         maxXSeenDebug=g.components.at(m).maxX;
            //     }
            // }
        }
    }
}

void SingleGuardAlgorithm::debugInitializeGuards(int numGuards, int height, tiledMatrix<elev_t>* elev){
    float nGRows=std::max(1.0,std::sqrt((numGuards)*(nrows/ncols)));
    Guard g1;
    g1.x=50;
    g1.z=50;
    g1.h=50;
    g1.r=20;
    g1.index=0;
    g1.findConnected();
    guards.push_back(g1);

    Guard g2;
    g2.x=55;
    g2.z=55;
    g2.h=50;
    g2.r=20;
    g2.index=0;
    g2.findConnected();
    guards.push_back(g2);

    bool result=ConnectedComponent::checkComponentsIntersection(&(guards.at(0).components.at(0)),&(guards.at(1).components.at(0)));
}
