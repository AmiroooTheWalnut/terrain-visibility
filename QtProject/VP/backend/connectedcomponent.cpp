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
        if(a->minX>=b->minX){
            int startingIndexB=binarySearchIndex(b,a->minX);
            for(int rb=startingIndexB;rb<startingIndexB+(minHigh-maxLow)-1;rb++){
                for(int startb=0;startb<b->colRangeInRow.at(rb).xStart.size();startb++){
                    for(int starta=0;starta<a->colRangeInRow.at(rb-startingIndexB).xStart.size();starta++){
                        if(b->colRangeInRow.at(rb).xStart.at(startb)<=a->colRangeInRow.at(rb-startingIndexB).xStart.at(starta) && a->colRangeInRow.at(rb-startingIndexB).xStart.at(starta)<=b->colRangeInRow.at(rb).xEnd.at(startb)){
                            return true;
                        }
                        if(a->colRangeInRow.at(rb-startingIndexB).xStart.at(starta)<=b->colRangeInRow.at(rb).xStart.at(startb) && b->colRangeInRow.at(rb).xStart.at(startb)<=a->colRangeInRow.at(rb-startingIndexB).xEnd.at(starta)){
                            return true;
                        }
                    }
                }
            }
        }else{
            int startingIndexA=binarySearchIndex(a,b->minX);
            for(int ra=startingIndexA;ra<startingIndexA+(minHigh-maxLow)-1;ra++){
                for(int startb=0;startb<b->colRangeInRow.at(ra-startingIndexA).xStart.size();startb++){
                    for(int starta=0;starta<a->colRangeInRow.at(ra).xStart.size();starta++){
                        if(b->colRangeInRow.at(ra-startingIndexA).xStart.at(startb)<=a->colRangeInRow.at(ra).xStart.at(starta) && a->colRangeInRow.at(ra).xStart.at(starta)<=b->colRangeInRow.at(ra-startingIndexA).xEnd.at(startb)){
                            return true;
                        }
                        if(a->colRangeInRow.at(ra).xStart.at(starta)<=b->colRangeInRow.at(ra-startingIndexA).xStart.at(startb) && b->colRangeInRow.at(ra-startingIndexA).xStart.at(startb)<=a->colRangeInRow.at(ra).xEnd.at(starta)){
                            return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

int ConnectedComponent::binarySearchIndex(ConnectedComponent *in, int targetRow){
    int min=0;
    int max=in->colRangeInRow.size();
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
