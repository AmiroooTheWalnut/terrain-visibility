#include <iostream>
#include <unordered_set>
#include "singleguardalgorithm.h"

SingleGuardAlgorithm::SingleGuardAlgorithm() {
}

void SingleGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType){
    guards=initializeGuards(numGuards,height,radius,elev,initGuardType);
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
            for(int g=0;g<guards.size()&&isEndAchieved==false;g++)
            {
                Guard *guard = &(guards.at(g));
                for(int c=0;c<guard->components.size()&&isEndAchieved==false;c++)
                {
                    ConnectedComponent *gConComp=&(guard->components.at(c));
                    if(gConComp->isComponentUsedForFrontier==false)
                    {
                        //for(int of=prevFrontierIndex;of>=0;of--)//*** Index for other frontiers (potentially redundant because we only need to check with last frontier)
                        //{
                            for(int cp=0;cp<pFrontier.at(prevFrontierIndex).size()&&isEndAchieved==false;cp++)//Connected component index from previous frontier
                            {
                                ConnectedComponent *ofConComp=pFrontier.at(prevFrontierIndex).at(cp);//Connected component from previous frontier
                                if(ConnectedComponent::checkComponentsIntersection(gConComp,ofConComp))
                                {
                                    gConComp->intersectingCC.push_back(ofConComp);
                                    //ofConComp->intersectingCC.push_back(gConComp);//Only backward path is needed, this is redundant
                                    constructingFrontier.push_back(gConComp);
                                    gConComp->isComponentUsedForFrontier=true;//Block this connected component from being added later
                                    successToAddPremiter=true;
                                    //cout<<gConComp->maxX<<endl;
                                    if(gConComp->maxX==trueNRows-1)
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
                        //}
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
        cout << "Returning Path:" << endl;
        for(int f=0;f<returningPath.size();f++){
            //cout << "Frontier: " << f << endl; - It is not frontier index, remove this for clarification
            cout << "   Guard: " << returningPath.at(f)->owner->index << endl;
        }
        cout << "Frontier Details:" << endl;
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

        cout<<"End of single Guard frontier algorithm"<<endl;

    }
}

bool SingleGuardAlgorithm::constructF0(std::vector<Guard> *guards, std::vector<std::vector<ConnectedComponent *>> *pFrontier, tiledMatrix<elev_t>* elev){
    //Initialize all connected components (isComponentUsedForFrontier variable to false)
    for(int g=0;g<guards->size();g++){
        Guard *guard = &guards->at(g);
        for(int c=0;c<guard->components.size();c++){
            guard->components.at(c).isComponentUsedForFrontier=false;
        }
    }
    bool isEndFound=false;//Checks if the algorithm should finish with a single guard that sees north to south
    std::vector<ConnectedComponent *> f0;
    for(int g=0;g<guards->size();g++){
        Guard *guard = &guards->at(g);
        for(int c=0;c<guard->components.size();c++){
            if(guard->components.at(c).minX==0){//Guard can see north with connected component "c"
                if(guard->components.at(c).maxX==trueNRows-1){//Guard can see the end (south)
                    isEndFound=true;
                }
                f0.push_back(&(guard->components.at(c)));
                guard->components.at(c).isComponentUsedForFrontier=true;//Make sure this connected component won't be used for later frontiers
            }
        }
    }
    pFrontier->push_back(f0);
    return isEndFound;//Return boolean indicating if a single guard is enough
}

std::vector<Guard> SingleGuardAlgorithm::initializeGuardsFib(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev){
    std::vector<Guard> localGuards;
    int counter=0;
    for(int i=1;i<=numGuards;i++){
        Guard *g=new Guard();
        std::pair<float,float> out=fibonacciLattice(counter+1,numGuards+1);
        g->x=(int)(out.first*trueNCols);
        g->z=(int)(out.second*trueNRows);
        cout<<"X: "<<g->x<<endl;
        cout<<"Z: "<<g->z<<endl;
        g->h=height;
        g->r=radius;
        g->index=counter;
        g->findConnected();
        localGuards.push_back(*g);
        counter=counter+1;
    }

    return localGuards;

}

std::vector<Guard> SingleGuardAlgorithm::initializeGuardsSquareUniform(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev){
    std::vector<Guard> localGuards;
    float nGRows=std::max(1.0,std::sqrt((numGuards)*(trueNRows/trueNCols)));
    float nGCols=std::max(1.0,std::sqrt((numGuards)*(trueNCols/trueNRows)));

    float nRowGuardPixels=std::floor(std::max(1.0f,((float)trueNCols/(float)(nGCols+1))));
    float nColGuardsPixels=std::floor(std::max(1.0f,((float)trueNRows/(float)(nGRows+1))));

    //int maxXSeenDebug=0;

    int counter=0;
    for(int i=1;i<=nGRows;i++){
        for(int j=1;j<=nGCols;j++){
            Guard *g=new Guard();
            g->x=i*nRowGuardPixels;
            g->z=j*nColGuardsPixels;
            g->h=height;
            g->r=radius;
            g->index=counter;
            g->findConnected();
            localGuards.push_back(*g);
            counter=counter+1;
            // if(counter==4){
            //     break;
            // }
            // for(int m=0;m<g.components.size();m++){
            //     if(maxXSeenDebug<g.components.at(m).maxX){
            //         maxXSeenDebug=g.components.at(m).maxX;
            //     }
            // }
        }
        // if(counter==4){
        //     break;
        // }
    }
    return localGuards;
}

std::vector<Guard> SingleGuardAlgorithm::initializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType){
    std::vector<Guard> guardsLocal;
    if(initGuardType=="Fib"){
        guardsLocal=initializeGuardsFib(numGuards,height,radius,elev);
    }
    if(initGuardType=="SqUniform"){
        guardsLocal=initializeGuardsSquareUniform(numGuards,height,radius,elev);
    }

    return guardsLocal;
}

void SingleGuardAlgorithm::debugInitializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev){
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

/*
 * Find the location of a guard based on Fibonacci Lattice. The index of guard and total number of guards are the inputs.
 */
std::pair<float,float> SingleGuardAlgorithm::fibonacciLattice(uint32_t input, uint32_t nunItems)
{
    float x = ((float)(input)) / SingleGuardAlgorithm::gR;
    x -= int(x);
    float y = ((float)(input)) / ((float)(nunItems));
    return std::pair(x, y);
}
