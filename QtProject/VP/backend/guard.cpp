#include "guard.h"

#include "connectedcomponent.h"
#include "tiledMatrix.h"
#include "TiledVS.h"


tiledMatrix<unsigned char>* pVisited=NULL;
tiledMatrix<unsigned char>* pGrid=NULL;
int row_num;
int col_num;

Guard::Guard() {
}

void Guard::findConnected(void) {
    /* Construct the connected components per guard based on the viewshed information */
    //char strX[10], strH[10], strZ[10], strR[10];

    std::string strX = std::to_string(x);
    //const char* obsX_p = strX;
    std::string strH = std::to_string(h);
    //const char* obsY_p = strH;
    std::string strZ = std::to_string(z);
    //const char* obsH_p = strZ;
    std::string strR = std::to_string(r);
    //const char* range_p = strR;
    const char *options[9]={"","1201","1201",strX.c_str(),strZ.c_str(),strH.c_str(),strR.c_str(),in_file.c_str(),"100"};

    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);
    Calc_Vis();
    /* Read viewshedp to figure out Connected Components */

    row_num = ((nrows + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
    col_num = ((ncols + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;

    if (pVisited) delete pVisited;
    if (pGrid) delete pGrid;
    pVisited = new tiledMatrix<unsigned char>(row_num, row_num, blockSizeRows, blockSizeCols, numBlocks, "tiles/visited");
    pGrid = new tiledMatrix<unsigned char>(row_num, row_num, blockSizeRows, blockSizeCols, numBlocks, "tiles/visited");
    pGrid->set(0);
    /* Make a copy of viewshedp -- Should be able to copy easier but I can't read the Spanish comments! */
    for(int i=0;i<nrows;i++)
    {
        for(int j=0;j<ncols;j++)
        {
            if (viewshedp->get(i,j))
                pGrid->set(i,j,1);
        }
    }

    bool done = false;
    while (!done)
    {
        /* Find a non-zero pixel to start */
        bool found = false;
        for(int i=0;i<nrows;i++)
        {
            for(int j=0;j<ncols;j++)
            {
                if (pGrid->get(i,j))
                {
                    pVisited->set(0);
                    floodFillCC(i, j);
                    /* After flood fill, we have a grid with the connected pixels set */
                    /* Now place it into a connected component format */
                    setConnectedComponent();
                    found = true;
                }
            }
        }
        /* Done when we cannot find a non-zero pixel */
        if (!found) done = true;
    }
}

/* Flood fill the grid pVisited with only the connected pixels */
void Guard::floodFillCC(int i, int j)
{
    if ((i < 0 || i >= row_num || j < 0 || j >= col_num)
        || pGrid->get(i, j) == 0 || pVisited->get(i, j))
        return;

    pVisited->set(i, j, 1);
    pGrid->set(i,j,0); /* Clear the pixel on pGrid so we won't find it again */

    floodFillCC(i, j+1);
    floodFillCC(i, j-1);
    floodFillCC(i-1, j);
    floodFillCC(i+1, j);
}

/* Put connected component data in the correct format */
void Guard::setConnectedComponent(void)
{
    ConnectedComponent *component = new ConnectedComponent();

    for(int i=0;i<nrows;i++)
    {
        bool lastSet = false;
        int startPos = 0;
        for (int j=0;j<ncols;j++)
        {
            if (pVisited->get(i,j))
            {
                if (!lastSet) startPos = j;
                lastSet = true;
            }
            else
            {
                if (startPos != 0)
                {
                    ConnectedRow conR;
                    conR.compRow = i;
                    conR.xStart = startPos;
                    conR.xEnd = j-1;
                    component->colRangeInRow.push_back(conR);
                    startPos = 0;
                }
                lastSet = false;
            }
        }
    }
    perimeter.push_back(*component);
}

int compRow;
int xStart;
int xEnd;
