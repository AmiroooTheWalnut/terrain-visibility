#include "guard.h"

#include "connectedcomponent.h"
#include "tiledMatrix.h"
#include "TiledVS.h"

bool debugFlag=false;

/* To avoid stack overflow */
uint16_t MaxIterations=6;

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

    //if (pVisited) delete pVisited;
    // pVisited=new vector<vector<unsigned char>>(nrows, vector<unsigned char> (ncols, 0));
    //vector<vector<unsigned char>> pVisitedLocal(nrows, vector<unsigned char> (ncols, 0));
    //pVisited=&pVisitedLocal;

    //int row_num = ((nrows + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
    //int col_num = ((ncols + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;

    //tiledMatrix<unsigned char> viewshedTrunkp = tiledMatrix<unsigned char>(row_num, row_num, blockSizeRows, blockSizeCols, numBlocks, "tiles/vistrunc");
    //Deep copy of entire viewshed because the side of viewshed can exceed elev and it can be less too.
    //for(int i=0;i<elevp->nrows;i++){
    //    for(int j=0;j<elevp->ncolumns;j++){
    //        viewshedTrunkp.set(i,j,viewshedp->get(i,j));
    //    }
    //}
    /* Read viewshedp to figure out Connected Components */

    //if (pVisited) delete pVisited;
    //if (pGrid) delete pGrid;

    // if(index==3){
    //     cout<<"DEBUGGG!!!!"<<endl;
    //     debugFlag=true;
    // }

    //vector<vector<unsigned char>> pGrid(viewshedp->nrows, vector<unsigned char> (viewshedp->ncolumns, 0));
    bool done = false;
    while (!done)
    {
        /* Find a non-zero pixel to start */
        bool found = false;
        for(uint16_t i=0;i<nrows;i++)
        {
            for(uint16_t j=0;j<ncols;j++)
            {
                if (viewshedp->get(i,j))
                {
                    vector<vector<unsigned char>> pVisitedLocal(nrows, vector<unsigned char> (ncols, 0));
                    pVisited=&pVisitedLocal;
                    //pVisited->set(0);
                    floodFillCC(i, j, 0);
                    /* After flood fill, we have a grid with the connected pixels set */
                    /* Now place it into a connected component format */
                    setConnectedComponent(pVisited);
                    found = true;
                }
            }
        }
        if (!found) done = true;
    }
    //delete pVisited;

    // row_num = ((nrows + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
    // col_num = ((ncols + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;


    // if (pVisited) delete pVisited;
    // if (pGrid) delete pGrid;
    // pVisited = new tiledMatrix<unsigned char>(row_num, row_num, blockSizeRows, blockSizeCols, numBlocks, "tiles/visited");
    // pGrid = new tiledMatrix<unsigned char>(row_num, row_num, blockSizeRows, blockSizeCols, numBlocks, "tiles/visited");
    // pGrid->set(0);
    // /* Make a copy of viewshedp -- Should be able to copy easier but I can't read the Spanish comments! */
    // for(int i=0;i<nrows;i++)
    // {
    //     for(int j=0;j<ncols;j++)
    //     {
    //         if (viewshedp->get(i,j))
    //             pGrid->set(i,j,1);
    //     }
    // }

    // bool done = false;
    // while (!done)
    // {
    //     /* Find a non-zero pixel to start */
    //     bool found = false;
    //     for(int i=0;i<nrows;i++)
    //     {
    //         for(int j=0;j<ncols;j++)
    //         {
    //             if (pGrid->get(i,j))
    //             {
    //                 pVisited->set(0);
    //                 floodFillCC(i, j);
    //                 /* After flood fill, we have a grid with the connected pixels set */
    //                 /* Now place it into a connected component format */
    //                 setConnectedComponent();
    //                 found = true;
    //             }
    //         }
    //     }
    //     /* Done when we cannot find a non-zero pixel */
    //     if (!found) done = true;
    // }
}

/* Flood fill the grid pVisited with only the connected pixels */
void Guard::floodFillCC(uint16_t i, uint16_t j, uint16_t level)
{
    if ((i < 0 || i >= pVisited->size() || j < 0 || j >= pVisited->at(0).size()) || viewshedp->get(i,j) == 0 || pVisited->at(i).at(j)!=0)
        return;

    pVisited->at(i).at(j)= 1;
    viewshedp->set(i,j,0); /* Clear the pixel on pGrid so we won't find it again */
    level++;
    if (level >= MaxIterations) return;

    floodFillCC(i, j+1, level);
    floodFillCC(i, j-1, level);
    floodFillCC(i-1, j, level);
    floodFillCC(i+1, j, level);
}

/* Put connected component data in the correct format */
void Guard::setConnectedComponent(vector<vector<unsigned char>> *pVisited)
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
        ConnectedRow conR;
        conR.compRow = i;
        for (int j=0;j<ncols;j++)
        {
            if (pVisited->at(i).at(j)==1 && j<ncols-1)
            {
                if (!lastSet) startPos = j;
                lastSet = true;
            }
            else if((j==ncols-1 && pVisited->at(i).at(j)==1)||pVisited->at(i).at(j)==0)// If visited columns in the row never ends or if it ends
            {
                if (startPos != -1)
                {
                    conR.xStart.push_back(startPos);
                    if(j==ncols-1 && pVisited->at(i).at(j)==1){
                        conR.xEnd.push_back(j);
                        if(maxZ<j){
                            maxZ=j;
                        }
                    }else{
                        conR.xEnd.push_back(j-1);
                        if(maxZ<j-1){
                            maxZ=j-1;
                        }
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

