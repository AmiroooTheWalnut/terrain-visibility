#include "guard.h"

#include "connectedcomponent.h"
#include "tiledMatrix.h"
#include "TiledVS.h"

bool debugFlag=false;

Guard::Guard() {
}

void Guard::findConnected(void) {
    /* Construct the connected components per guard based on the viewshed information */
    std::string strX = std::to_string(x);
    std::string strH = std::to_string(h);
    std::string strZ = std::to_string(z);
    std::string strR = std::to_string(r);
    const char *options[9]={"","1201","1201",strX.c_str(),strZ.c_str(),strH.c_str(),strR.c_str(),in_file.c_str(),"100"};

    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);
    Calc_Vis();

    bool done = false;
    while (!done)
    {
        /* Find a non-zero pixel to start */
        bool found = false;
        for(uint16_t i=0;i<nrows;i++)
        {
            for(uint16_t j=0;j<ncols;j++)
            {
                if (viewshedp->get(i,j)==1)
                {
                    floodFill(i, j);
                    /* After flood fill, we have a grid with the connected pixels set */
                    /* Now place it into a connected component format */
                    setConnectedComponent();
                    found = true;
                }
            }
        }
        if (!found) done = true;
    }
}

/* Flood fill the grid with only the connected pixels */
void Guard::floodFill(uint16_t sr, uint16_t sc)
{
    std::queue<std::pair<int, int>>q;
    q.push({sr, sc});

    while (!q.empty())
    {
        int r = q.front().first;
        int c = q.front().second;
        q.pop();
        if (r<0 || r>=nrows || c<0 || c>=ncols || viewshedp->get(r,c)!=1)
            continue;

        // Set a new color
        viewshedp->set(r,c,2);

        q.push({r+1, c});
        q.push({r-1, c});
        q.push({r, c+1});
        q.push({r, c-1});
    }
}

/* Put connected component data in the correct format */
void Guard::setConnectedComponent(void)
{
    ConnectedComponent component;
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
            if (viewshedp->get(i,j)==2 && j<ncols-1)
            {
                if (!lastSet) startPos = j;
                lastSet = true;
            }
            else if((j==ncols-1 && viewshedp->get(i,j)==2)||viewshedp->get(i,j)!=2)// If visited columns in the row never ends or if it ends
            {
                if (startPos != -1)
                {
                    conR.xStart.push_back(startPos);
                    if(j==ncols-1 && viewshedp->get(i,j)==2)
                    {
                        endPos = j;
                    }else
                    {
                        endPos = j-1;
                    }
                    conR.xEnd.push_back(endPos);
                    if(maxZ<endPos){
                        maxZ=endPos;
                    }

                    if(minZ>startPos){
                        minZ=startPos;
                    }
                    if(maxX<i){
                        maxX=i;
                    }
                    if(minX>i){
                        minX=i;
                    }

                    startPos = -1;
                    endPos = -1;

                    for (int k=startPos; k<= endPos; k++)
                        viewshedp->set(i,k,0); /* Clear pixel after setting the ConnectedRow */
                }
                lastSet = false;
            }
        }
        if(conR.xStart.size()>0){
            component.colRangeInRow.push_back(conR);
        }
    }
    component.maxX=maxX;
    component.minX=minX;
    component.maxZ=maxZ;
    component.minZ=minZ;
    component.owner=this;
    components.push_back(component);
}

