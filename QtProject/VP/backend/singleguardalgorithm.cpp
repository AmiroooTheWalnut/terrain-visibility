#include "singleguardalgorithm.h"

SingleGuardAlgorithm::SingleGuardAlgorithm() {

}

void SingleGuardAlgorithm::run(int numGuards, int height, tiledMatrix<elev_t>* elev){
    initializeGuardsUniform(numGuards,height,elev);
}

void SingleGuardAlgorithm::initializeGuardsUniform(int numGuards, int height, tiledMatrix<elev_t>* elev){
    float nGRows=std::max(1.0,std::sqrt((numGuards)*(nrows/ncols)));
    float nGCols=std::max(1.0,std::sqrt((numGuards)*(ncols/nrows)));

    float nRowGuardPixels=std::max(1.0f,((float)ncols/(float)(nGCols+1)));
    float nColGuardsPixels=std::max(1.0f,((float)nrows/(float)(nGRows+1)));

    int counter=0;
    for(int i=nRowGuardPixels;i<ncols-1;i=i+nRowGuardPixels){
        for(int j=nColGuardsPixels;j<nrows-1;j=j+nColGuardsPixels){
            Guard *g=new Guard();
            g->x=i;
            g->z=j;
            g->h=elev->get(i,j);
            g->index=counter;
            guards.push_back(*g);
            counter=counter+1;
        }
    }

    cout<<"!!"<<endl;
}
