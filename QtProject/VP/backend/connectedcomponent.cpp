#include "connectedcomponent.h"

ConnectedComponent::ConnectedComponent() {}

ConnectedComponent ConnectedComponent::connectTwoComponents(ConnectedComponent *a, ConnectedComponent *b){

}

bool ConnectedComponent::checkComponentsIntersection(ConnectedComponent *a, ConnectedComponent *b){
    // int minHigh=std::min(a.colRangeInRow.back().compRow,b.colRangeInRow.back().compRow);
    // int maxLow=std::max(a.colRangeInRow.at(0).compRow,b.colRangeInRow.at(0).compRow);
    int minHigh=std::min(a->maxX,b->maxX);
    int maxLow=std::max(a->minX,b->minX);
    if(minHigh<maxLow){
        return false;
    }else{
        if(a->minX>=b->minX){//Check which connected component is ahead
            int startingIndexB=binarySearchIndex(b,a->minX);//Find the index of row in b that refers to the start of a
            for(int rb=startingIndexB;rb<startingIndexB+(minHigh-maxLow)-1;rb++)//Iterate through rows in b that share X with a
            {
                ConnectedRow *rowB = &b->colRangeInRow.at(rb);
                ConnectedRow *rowA = &a->colRangeInRow.at(rb-startingIndexB);
                for(int startb=0; startb<rowB->xStart.size(); startb++)//Iterate though start/end values for b
                {
                    for(int starta=0;starta<rowA->xStart.size();starta++)//Iterate though start/end values for a
                    {
                        //Check if start of a is in the middle of start and end of b
                        if(rowB->xStart.at(startb)<=rowA->xStart.at(starta) &&
                            rowA->xStart.at(starta)<=rowB->xEnd.at(startb)) {
                            return true;
                        }
                        //Check if start of b is in the middle of start and end of a
                        if(rowA->xStart.at(starta)<=rowB->xStart.at(startb) &&
                            rowB->xStart.at(startb)<=rowA->xEnd.at(starta)) {
                            return true;
                        }
                    }
                }
            }
        }else{//Check which connected component is ahead
            int startingIndexA=binarySearchIndex(a,b->minX);//Find the index of row in a that refers to the start of b
            for(int ra=startingIndexA;ra<startingIndexA+(minHigh-maxLow)-1;ra++)//Iterate through rows in a that share X with b
            {
                ConnectedRow *rowA = &a->colRangeInRow.at(ra);
                ConnectedRow *rowB = &b->colRangeInRow.at(ra-startingIndexA);
                for(int startb=0;startb<rowB->xStart.size();startb++)//Iterate though start/end values values for b
                {
                    for(int starta=0;starta<rowA->xStart.size();starta++)//Iterate though start/end values for a
                    {
                        //Check if start of a is in the middle of start and end of b
                        if(rowB->xStart.at(startb)<=rowA->xStart.at(starta) &&
                            rowA->xStart.at(starta)<=rowB->xEnd.at(startb)) {
                            return true;
                        }
                        //Check if start of b is in the middle of start and end of a
                        if(rowA->xStart.at(starta)<=rowB->xStart.at(startb) &&
                            rowB->xStart.at(startb)<=rowA->xEnd.at(starta)) {
                            return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

/*
 * Search in a connected component to find the target row index by the target row value.
 * Input is a connected component and a target row value
 * Output is the target row index in input connected component
 */
int ConnectedComponent::binarySearchIndex(ConnectedComponent *in, int targetRow){
    int min=0;
    int max=in->colRangeInRow.size()-1;
    while (min <= max) {
        int mid = min + (max - min) / 2;
        if (in->colRangeInRow.at(mid).compRow == targetRow)
            return mid;
        if (in->colRangeInRow.at(mid).compRow < targetRow)
            min = mid + 1;
        else
            max = mid - 1;
    }
    return -1;
}
