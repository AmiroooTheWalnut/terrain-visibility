#include "connectedcomponent.h"

ConnectedComponent::ConnectedComponent() {}

// Merge two components to one.
// Assume the caller has already checked that the two components intersects.
ConnectedComponent *ConnectedComponent::connectTwoComponents(ConnectedComponent *a, ConnectedComponent *b)
{
    std::vector<std::vector<bool>> bitmap(nrows,std::vector<bool>(ncols));

    unwrapComponent(a, &bitmap);
    unwrapComponent(b, &bitmap);
    ConnectedComponent *cc=setConnectedComponent(&bitmap);
    return cc;
}

// Unwrap component into a bitmap
void ConnectedComponent::unwrapComponent(ConnectedComponent *cc, std::vector<std::vector<bool>> *bitmap)
{
    for(int i=0;i<cc->colRangeInRow.size();i++)
    {
        ConnectedRow row=cc->colRangeInRow.at(i);
        for(int j=0;j<row.xStart.size();j++)
        {
            for(int c=row.xStart.at(j);c<row.xEnd.at(j);c++)
            {
                (*bitmap)[row.compRow][c]=1;
            }
        }
    }
}

// Convert a bitmap into a Connected Component with one or more ConnectedRows.
// Pass pointer to bitmap instead of bitmap to save stack and avoid copying
ConnectedComponent* ConnectedComponent::setConnectedComponent(std::vector<std::vector<bool>> *bitmap)
{
    ConnectedComponent *component=new ConnectedComponent();
    int maxX=-100000;
    int minX=100000;
    int maxZ=-100000;
    int minZ=100000;
    for(int i=0;i<nrows;i++)
    {
        bool lastSet = false;
        int startPos = -1;
        int endPos = -1;
        ConnectedRow conR;
        conR.compRow = i;
        for (int j=0;j<ncols;j++)
        {
            if (bitmap->at(i).at(j)==1 && j<ncols-1)
            {
                if (!lastSet) startPos = j;
                lastSet = true;
            }
            else if((j==ncols-1 && bitmap->at(i).at(j)==1)||bitmap->at(i).at(j)!=1)// If visited columns in the row never ends or if it ends
            {
                if (startPos != -1)
                {
                    conR.xStart.push_back(startPos);
                    if(j==ncols-1 && bitmap->at(i).at(j)==1)
                    {
                        endPos = j;
                    }else
                    {
                        endPos = j-1;
                    }
                    conR.xEnd.push_back(endPos);
                    if(maxZ<endPos)
                    {
                        maxZ=endPos;
                    }

                    if(minZ>startPos)
                    {
                        minZ=startPos;
                    }
                    if(maxX<i)
                    {
                        maxX=i;
                    }
                    if(minX>i)
                    {
                        minX=i;
                    }

                    for (int k=startPos; k<= endPos; k++)
                    {
                        (*bitmap)[i][k]=0; /* Clear pixel after setting the ConnectedRow */
                    }
                    startPos = -1;
                    endPos = -1;
                }
                lastSet = false;
            }
        }
        if(conR.xStart.size()>0)
        {
            component->colRangeInRow.push_back(conR);
        }
    }
    component->maxX=maxX;
    component->minX=minX;
    component->maxZ=maxZ;
    component->minZ=minZ;
    //component.owner=this;
    //components.push_back(component);
    return component;
}

// Check that two components intersect
bool ConnectedComponent::checkComponentsIntersection(ConnectedComponent *a, ConnectedComponent *b)
{
    // int minHigh=std::min(a.colRangeInRow.back().compRow,b.colRangeInRow.back().compRow);
    // int maxLow=std::max(a.colRangeInRow.at(0).compRow,b.colRangeInRow.at(0).compRow);
    int minHigh=std::min(a->maxX,b->maxX);
    int maxLow=std::max(a->minX,b->minX);
    if(minHigh<maxLow)
    {
        return false;
    }else
    {
        if(a->minX>=b->minX){//Check which connected component is ahead
            int startingIndexB=a->minX-b->minX;//Find the index of row in b that refers to the start of a
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
                            rowA->xStart.at(starta)<=rowB->xEnd.at(startb))
                        {
                            return true;
                        }
                        //Check if start of b is in the middle of start and end of a
                        if(rowA->xStart.at(starta)<=rowB->xStart.at(startb) &&
                            rowB->xStart.at(startb)<=rowA->xEnd.at(starta))
                        {
                            return true;
                        }
                    }
                }
            }
        }else
        {//Check which connected component is ahead
            int startingIndexA=b->minX-a->minX;//Find the index of row in a that refers to the start of b
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
                            rowA->xStart.at(starta)<=rowB->xEnd.at(startb))
                        {
                            return true;
                        }
                        //Check if start of b is in the middle of start and end of a
                        if(rowA->xStart.at(starta)<=rowB->xStart.at(startb) &&
                            rowB->xStart.at(startb)<=rowA->xEnd.at(starta))
                        {
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
int ConnectedComponent::binarySearchIndex(ConnectedComponent *in, int targetRow)
{
    int min=0;
    int max=in->colRangeInRow.size()-1;
    while (min <= max)
    {
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
