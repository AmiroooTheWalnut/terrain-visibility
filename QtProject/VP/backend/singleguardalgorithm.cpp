#include <iostream>
#include <fstream>
#include <unordered_set>
#include "singleguardalgorithm.h"

SingleGuardAlgorithm::SingleGuardAlgorithm()
{
}

bool SingleGuardAlgorithm::run(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType, int pairingOrder)
{
    bool retVal = true;

    Print_Time((char*)"SingleGuardAlgorithm::run start");

    //debugInitializeGuards(numGuards,height,elev);
    bool isEndAchieved=constructF0(elev);
    if(frontier.size()==0)
    {
        cout<<"No solution exists! Failed to construct F0."<<endl;
        retVal = false;
    }
    if (isEndAchieved)
    {
        cout<<"F0 reached the South!"<<endl;
    }
    if(isEndAchieved==false && retVal)
    {
        std::vector<ConnectedComponent*> returningPath;
        bool successToAddPremiter=true;
        int prevFrontierIndex=0;
        std::vector<ConnectedComponent *> prevFrontier = frontier.at(0);

        while(successToAddPremiter==true && isEndAchieved==false && retVal)
        {
            successToAddPremiter=false;
            std::vector<ConnectedComponent *> constructingFrontier;//Currently constructing frontier

            for (Guard *guard : guards)
            {
                for (ConnectedComponent *gConComp : guard->components)
                {
                    if(!gConComp->isComponentUsedForFrontier)
                    {
                        for (ConnectedComponent *ofConComp : prevFrontier)//Connected component index from previous frontier
                        {
                            if(ConnectedComponent::checkComponentsIntersection(gConComp,ofConComp))
                            {
                                gConComp->intersectingCC.push_back(ofConComp);
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
                        if(isEndAchieved)
                        {
                            break;
                        }
                    }
                    if (isEndAchieved) break;
                }
                if (isEndAchieved) break;
            }
            if(successToAddPremiter==true)
            {
                frontier.push_back(constructingFrontier);
                prevFrontierIndex=prevFrontierIndex+1;
                prevFrontier = constructingFrontier;
            }
        }
        if(returningPath.size()==0)
        {
            cout<<"No solution exists! There is no path from north to south."<<endl;
            retVal = false;
        }
        while(retVal && !(returningPath.back()->intersectingCC.empty()))
        {
            returningPath.push_back(returningPath.back()->intersectingCC.at(0));
        }
        cout << "Returning Path:" << endl;

        for (ConnectedComponent *cc : returningPath)
        {
            //cout << "Frontier: " << f << endl; - It is not frontier index, remove this for clarification
            cout << "   Guard: " << cc->owner->index << endl;
        }
        cout << "Frontier Details:" << endl;

        for(int f=0;f<frontier.size();f++)
        {
            cout << "Frontier: " << f << endl;

            std::unordered_set<int> guardsIndexSet;
            for(int c=0;c<frontier.at(f).size();c++)
            {
                guardsIndexSet.insert(frontier.at(f).at(c)->owner->index);
            }
            cout << "   Guards: " << endl;
            unordered_set<int>::iterator itr;
            for (itr = guardsIndexSet.begin(); itr != guardsIndexSet.end();itr++)
                cout << (*itr) << endl;
        }
        cout<<"End of single Guard frontier algorithm"<<endl;

    }
    Print_Time((char*)"SingleGuardAlgorithm::run end");

    return retVal;
}

bool SingleGuardAlgorithm::constructF0(tiledMatrix<elev_t>* elev)
{
    //Initialize all connected components (isComponentUsedForFrontier variable to false)

    for (Guard *g : guards)
    {
        g->resetUsedForFrontier();
    }

    bool isEndFound=false;//Checks if the algorithm should finish with a single guard that sees north to south
    std::vector<ConnectedComponent *> f0;

    for (Guard *g : guards)
    {
        for (ConnectedComponent *c: g->components)
        {
            if(c->minX==0){//Guard can see north with connected component "c"
                if(c->maxX==trueNRows-1)
                {//Guard can see the end (south)
                    isEndFound=true;
                }
                f0.push_back(c);
                c->isComponentUsedForFrontier=true;//Make sure this connected component won't be used for later frontiers
            }
        }
    }
    frontier.push_back(f0);
    return isEndFound;//Return boolean indicating if a single guard is enough
}

void SingleGuardAlgorithm::initializeGuardsFib(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev)
{
    int counter=0;
    for(int i=1;i<=numGuards;i++)
    {
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
        guards.push_back(g);
        counter=counter+1;
    }
}

void SingleGuardAlgorithm::initializeGuardsSquareUniform(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev)
{
    float nGRows=std::max(1.0,std::sqrt((numGuards)*(trueNRows/trueNCols)));
    float nGCols=std::max(1.0,std::sqrt((numGuards)*(trueNCols/trueNRows)));

    float nRowGuardPixels=std::floor(std::max(1.0f,((float)trueNCols/(float)(nGCols+1))));
    float nColGuardsPixels=std::floor(std::max(1.0f,((float)trueNRows/(float)(nGRows+1))));

    //int maxXSeenDebug=0;

    int counter=0;
    for(int i=1;i<=nGRows;i++)
    {
        for(int j=1;j<=nGCols;j++)
        {
            Guard *g=new Guard();
            g->x=i*nRowGuardPixels;
            g->z=j*nColGuardsPixels;
            g->h=height;
            g->r=radius;
            g->index=counter;
            g->findConnected();
            guards.push_back(g);
            counter=counter+1;
            // if(counter==4){
            //     break;
            // }
            // for(int m=0;m<g.components.size();m++){
            //     if(maxXSeenDebug<g.components.at(m)->maxX){
            //         maxXSeenDebug=g.components.at(m)->maxX;
            //     }
            // }
        }
        // if(counter==4){
        //     break;
        // }
    }
}

void SingleGuardAlgorithm::initializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev, std::string initGuardType)
{
    Print_Time((char*)"SingleGuardAlgorithm::initializeGuards start");

    reset(); // Clear all memory before we start over

    if(initGuardType=="Fib")
    {
        initializeGuardsFib(numGuards,height,radius,elev);
    }
    if(initGuardType=="SqUniform")
    {
        initializeGuardsSquareUniform(numGuards,height,radius,elev);
    }
}

void SingleGuardAlgorithm::debugInitializeGuards(int numGuards, int height, int radius, tiledMatrix<elev_t>* elev)
{
    Guard *g1 = new(Guard);
    g1->x=50;
    g1->z=50;
    g1->h=50;
    g1->r=20;
    g1->index=0;
    g1->findConnected();
    guards.push_back(g1);

    Guard *g2 = new(Guard);
    g2->x=55;
    g2->z=55;
    g2->h=50;
    g2->r=20;
    g2->index=0;
    g2->findConnected();
    guards.push_back(g2);

    bool result=ConnectedComponent::checkComponentsIntersection(guards.at(0)->components.at(0),guards.at(1)->components.at(0));
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

void SingleGuardAlgorithm::exportForILP(std::string filename)
{
    Print_Time((char*)"exportForILP start");
    std::ofstream outputFile(filename);

    if (!outputFile) {
        std::cerr << "Error opening file for writing!" << std::endl;
        return;
    }

    // Fill out Connected Component index
    int cIndex = 0;
    for (Guard *g: guards)
    {
        for (ConnectedComponent *cc: g->components)
        {
            cc->cIndex = cIndex++;
        }
    }
    // Now output the Guards, their Connected Components, and Intersecting Connected Components.
    for (Guard *g: guards)
    {
        outputFile << "Guard " << g->index << std::endl;
        for (ConnectedComponent *cc: g->components)
        {
            outputFile << "ConnectedComponent " << cc->cIndex << std::endl;

            // Revisit intersecting
            // Cannot use intersectingCC which is impacted by F0
            for (Guard *gg: guards)
            {
                for (ConnectedComponent *dd: gg->components)
                {
                    if (dd != cc && ConnectedComponent::checkComponentsIntersection(cc, dd))
                    {
                        outputFile << "Intersecting " << dd->cIndex << std::endl;
                    }
                }
            }
        }
    }
    // Output the Connected Components that overlaps North and South
    for (Guard *g : guards)
    {
        for (ConnectedComponent *cc: g->components)
        {
            if(cc->minX==0)
            {
                outputFile << "CrossNorth " << cc->cIndex << std::endl;
            }
            if(cc->maxX==trueNRows-1)
            {
                outputFile << "CrossSouth " << cc->cIndex << std::endl;
            }
        }
    }

    // Close the file
    outputFile.close();

    cout << "Finished outputting file for ILP" << std::endl;
}

void  SingleGuardAlgorithm::reset(void)
{
    // Clear memory of Guard and ConnectedComponent
    for (Guard *g: guards)
    {
        g->reset();
    }

    guards.clear();
    guards.shrink_to_fit();

    // Clear std::vector of frontier
    for(int f=0;f<frontier.size();f++)
    {
        frontier.at(f).clear();
    }
    frontier.clear();

    guardsPaired = false;
}
