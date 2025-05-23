/**
 * Written by Amir Mohammad Esmaieeli Sikaroudi in November 2024.
 * This file connects the backend and frontend. This file is not put inside frontend folder because of compiler errors.
 * The functions for drawing the elevation map and viewshed are provided.
 */

#include <QQmlEngine>
#include <QQmlComponent>
#include <QTransform>
#include <QVariant>
#include <stdlib.h>
#include <QImageReader>
#ifdef Q_OS_WIN
    #include "opencv2/opencv.hpp"
    #include "opencv2/core/mat.hpp"
#else
    #include <opencv2/opencv.hpp>
    #include <opencv2/core/mat.hpp>
#endif
#include "BackendContainer.h"
//#include <QtGraphs/private/qquickgraphssurface_p.h>

BackendContainer::BackendContainer(QObject *parent)
    : QObject{parent}
{
    qRegisterMetaType<QSurface3DSeries *>();
    //qRegisterMetaType<QList<QSurface3DSeries> *>();
}

/*
 * This function calls the backend to calculate visibility and keeps a pointer to the results.
 * The size of the surface is fixed for now.
 */
void BackendContainer::readElevData(const QString file_name)
{
    std::string file_name_str = file_name.toStdString();
    const char* file_name_p = file_name_str.c_str();
    const char *options[9]={"","1201","1201","50","50","10","10",file_name_p,"100"};

    // run(8,options);
    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);
    Read_Elev();

    trueNRows=nrows;
    trueNCols=ncols;
    //nrows=std::max(nrows,ncols);
    //ncols=std::max(nrows,ncols);
    if (elevData)
    {
        delete(elevData);
    }
    elevData = elevp;
}

void BackendContainer::readElevImgData(const QString file_name)
{
    std::string file_name_str = file_name.toStdString();
    QImageReader reader(file_name);
    QImage img;
    if ( reader.canRead()) {
        img = reader.read();
        //QImage rotatedImg = img.transformed(QTransform().rotate(90.0));
        //tiledMatrix<elev_t> tempElev;
        nrows=img.width();
        ncols=img.height();
        trueNRows=nrows;
        trueNCols=ncols;
        //nrows=std::max(nrows,ncols);
        //ncols=std::max(nrows,ncols);
        int mem = 80;
        int cellsize = sizeof(elev_t) + sizeof(unsigned char);
        int numBlocks = (mem * 1024 * 1024) / (cellsize * blockSizeRows * blockSizeCols);
        int nrows_aux = ((img.width() + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
        int ncols_aux = ((img.height() + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;
        maxHeight=-1000000;
        minHeight=1000000;
        tiledMatrix<elev_t> *tempElev = new tiledMatrix<elev_t>(nrows_aux, ncols_aux, blockSizeRows, blockSizeCols, numBlocks, "tiles/_elev_");
        for(int i=0;i<trueNRows;i++){
            for(int j=0;j<trueNCols;j++){
                QColor color=img.pixelColor(i,j);
                int hVal = color.red();
                tempElev->set(j,i,hVal);
                if(maxHeight<hVal){
                    maxHeight=hVal;
                }
                if(minHeight>hVal){
                    minHeight=hVal;
                }
                //cout<<"i: "<<i<<" j: "<<j<<" "<<tempElev->get(i,j)<<endl;
            }
        }
        if (elevData)
        {
            delete(elevData);
        }
        elevData=tempElev;
        elevp=tempElev;
    } else{
        cout << "cannot read image"<<endl;
    }
}

/*
 * This function calls the backend to calculate visibility and keeps a pointer to the results.
 * The size of the surface is fixed for now.
 */
void BackendContainer::updateVisibility(QString obsX, QString obsY, QString obsH, QString range)
{
    std::string obsX_str = obsX.toStdString();
    const char* obsX_p = obsX_str.c_str();
    std::string obsY_str = obsY.toStdString();
    const char* obsY_p = obsY_str.c_str();
    std::string obsH_str = obsH.toStdString();
    const char* obsH_p = obsH_str.c_str();
    std::string range_str = range.toStdString();
    const char* range_p = range_str.c_str();
    std::string width_str = std::to_string(trueNRows);
    const char* width_p = width_str.c_str();
    std::string height_str = std::to_string(trueNCols);
    const char* height_p = height_str.c_str();
    const char *options[9]={"",height_p,width_p,obsX_p,obsY_p,obsH_p,range_p,in_file.c_str(),"100"};

    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);


    Calc_Vis();

    //int tempnCols=ncols;
    //ncols=nrows;
    //nrows=tempnCols;

    viewshedData=viewshedp;
}

/*
 * This function prepares the surface points and updates QSurface3DSeries and adds texture manually to the surface. The function returns some strings to be used in QML.
 * The size of the surface is returned.
*/
QList<QString> BackendContainer::drawSurface(QSurface3DSeries *series)
{
    QImage *texture=new QImage(trueNRows,trueNCols,QImage::Format_ARGB32);

    if(!surfaceData->isEmpty()){
        surfaceData->clear();
    }

    //QSurfaceDataArray *m_resetArray=new QSurfaceDataArray();
    for(int i=0;i<trueNCols;i++){
        QSurfaceDataRow *a=new QSurfaceDataRow();
        for(int j=0;j<trueNRows;j++){
            QSurfaceDataItem *d=new QSurfaceDataItem();
            int hValue=elevData->get(i,j);
            d->setX(j);
            d->setY(hValue);
            d->setZ(i);
            a->append(*d);
            delete d;
            float interpolatedHValue=(float)(hValue-minHeight)/(float)(maxHeight-minHeight);
            QColor c=interpolateColor(interpolatedHValue);
            texture->setPixelColor(j,i,c);
        }
        //m_resetArray->append(*a);
        surfaceData->append(*a);
        delete a;
    }
    //series->dataProxy()->resetArray();
    //series->dataProxy()->resetArray(*m_resetArray);
    series->dataProxy()->resetArray(*surfaceData);
    //series->dataProxy()->resetArray(*m_resetArray);
    QImage rotatedImg = texture->transformed(QTransform().rotate(0.0));
    series->setTexture(rotatedImg);

    QList<QString> qList;
    QString strHmax = QString::number(maxHeight);
    QString strHmin = QString::number(minHeight);
    QString strXmax = QString::number(nrows);
    QString strZmax = QString::number(ncols);
    qList.append(strHmax);
    qList.append(strHmin);
    qList.append(strXmax);
    qList.append(strZmax);

    delete(texture);

    return qList;
}

QList<QString> BackendContainer::drawViewSurface(QSurface3DSeries *series, QSurface3DSeries *vSeries, QString obsX, QString obsZ, QString obsH,QString range, int r,int g,int b)
{
    //vSeries->dataProxy()->resetArray()
    //vSeries->setSelectedPoint(NULL);
    //vSeries->dataProxy()->disconnect(vSeries->parent());
    //vSeries->clearArray();
    //vSeries->dataProxy()->resetArray();

    BackendContainer::drawSurface(series);

    QColor yColor(r,g,b);
    vSeries->setWireframeColor(yColor);
    updateVisibility(obsX,obsZ,obsH,range);
    QImage *texture=new QImage(ncols,nrows,QImage::Format_ARGB32);
    //QImage *vTexture=new QImage(2,2,QImage::Format_ARGB32);
    for(int i=0;i<nrows;i++){
        for(int j=0;j<ncols;j++){
            if(viewshedData->get(i,j)==0){
                int hValue=elevData->get(i,j);
                float interpolatedHValue=(float)(hValue-minHeight)/(float)(maxHeight-minHeight);
                QColor c=interpolateColor(interpolatedHValue);
                texture->setPixelColor(j,i,c);
            }else{
                //QColor c("red");
                texture->setPixelColor(j,i,yColor);
            }
        }
    }
    //QImage rotatedImg = texture->transformed(QTransform().rotate(90.0));
    series->setTexture(*texture);

    if(!viewerData->empty()){
        vSeries->clearArray();
        viewerData->clear();
    }


    //QSurfaceDataArray *m_viewerResetArray=new QSurfaceDataArray();
    int x=atoi(obsX.toStdString().c_str());
    int z=atoi(obsZ.toStdString().c_str());
    int sH=elevData->get(x,z);
    int y=atoi(obsH.toStdString().c_str())+sH;

    QSurfaceDataRow *a=new QSurfaceDataRow();
    QSurfaceDataItem *d=new QSurfaceDataItem();
    d->setX(z+viewerSize);
    d->setY(y);
    d->setZ(x+viewerSize);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z);
    d->setY(y);
    d->setZ(x+viewerSize);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z-viewerSize);
    d->setY(y);
    d->setZ(x+viewerSize);
    a->append(*d);
    delete d;
    viewerData->append(*a);
    delete a;

    a=new QSurfaceDataRow();
    d=new QSurfaceDataItem();
    d->setX(z+viewerSize);
    d->setY(y);
    d->setZ(x);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z);
    d->setY(y);
    d->setZ(x);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z-viewerSize);
    d->setY(y);
    d->setZ(x);
    a->append(*d);
    delete d;
    viewerData->append(*a);
    delete a;

    a=new QSurfaceDataRow();
    d=new QSurfaceDataItem();
    d->setX(z+viewerSize);
    d->setY(y);
    d->setZ(x-viewerSize);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z);
    d->setY(y);
    d->setZ(x-viewerSize);
    a->append(*d);
    delete d;
    d=new QSurfaceDataItem();
    d->setX(z-viewerSize);
    d->setY(y);
    d->setZ(x-viewerSize);
    a->append(*d);
    delete d;
    viewerData->append(*a);
    delete a;

    //vTexture->setPixelColor(0,7,c);

    //m_viewerResetArray->append(*a);


    //vSeries->clearArray();
    //vSeries->dataProxy()->resetArray(*m_viewerResetArray);

    //cout<<"!!!"<<vSeries->dataArray().size()<<endl;
    vSeries->dataProxy()->resetArray(*viewerData);


    //vSeries->dataProxy().
    //vSeries->dataProxy()->addRows(*m_viewerResetArray);
    //vSeries->dataProxy()->arrayReset();

    //series->dataProxy()->arrayReset();

    //vSeries->setTexture(*vTexture);

    QList<QString> qList;

    delete(texture);

    return qList;
}

void BackendContainer::drawViewBatchSurface(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, std::vector<Guard *> *guards, std::vector<QColor> *explicitColors)
{
    BackendContainer::drawSurface(series);
    QImage *texture=new QImage(ncols,nrows,QImage::Format_ARGB32);

    for(int i=0;i<nrows;i++){
        for(int j=0;j<ncols;j++){
            int hValue=elevData->get(i,j);
            float interpolatedHValue=(float)(hValue-minHeight)/(float)(maxHeight-minHeight);
            QColor c=interpolateColor(interpolatedHValue);
            texture->setPixelColor(j,i,c);
        }
    }

    int hueStep = 180 / vSeries.size();
    int saturation = 255; // Fixed saturation
    int value = 255;      // Fixed value

    for(int g=0;g<guards->size();g++){
        QColor yColor;
        if(explicitColors==NULL){
            int hue = g * hueStep;
            cv::Mat bgrMat;
            cv::Mat hsvMat(1, 1, CV_8UC3, cv::Scalar(hue, saturation, value));
            cv::cvtColor(hsvMat, bgrMat, cv::COLOR_HSV2BGR);
            cv::Vec3b temp=bgrMat.at<cv::Vec3b>(0,0);
            //cout<< hsvMat <<endl;
            yColor.setRed(temp.val[0]);
            yColor.setGreen(temp.val[1]);
            yColor.setBlue(temp.val[2]);
        }else{
            yColor=explicitColors->at(g);
        }
        vSeries.at(g)->setWireframeColor(yColor);
        QString obsX=QString::fromStdString(std::to_string(guards->at(g)->x));
        QString obsZ=QString::fromStdString(std::to_string(guards->at(g)->z));
        QString obsH=QString::fromStdString(std::to_string(guards->at(g)->h));
        QString range=QString::fromStdString(std::to_string(guards->at(g)->r));
        updateVisibility(obsX,obsZ,obsH,range);

        //QImage *vTexture=new QImage(2,2,QImage::Format_ARGB32);
        for(int i=0;i<nrows;i++){
            for(int j=0;j<ncols;j++){
                if(viewshedData->get(i,j)!=0){
                    texture->setPixelColor(j,i,yColor);
                }
            }
        }
        //QImage rotatedImg = texture->transformed(QTransform().rotate(90.0));


        QSurfaceDataArray *viewerData=new QSurfaceDataArray();

        //if(!viewerData->empty()){
        //    vSeries->at(i).clearArray();
        //    viewerData->clear();
        //}


        //QSurfaceDataArray *m_viewerResetArray=new QSurfaceDataArray();
        int x=atoi(obsX.toStdString().c_str());
        int z=atoi(obsZ.toStdString().c_str());
        int sH=elevData->get(x,z);
        int y=atoi(obsH.toStdString().c_str())+sH;

        QSurfaceDataRow *a=new QSurfaceDataRow();
        QSurfaceDataItem *d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        a=new QSurfaceDataRow();
        d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        a=new QSurfaceDataRow();
        d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        vSeries.at(g)->dataProxy()->resetArray(*viewerData);
    }
    series->setTexture(*texture);

    delete(texture);
}

void BackendContainer::drawFrontiers(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, std::vector<std::vector<ConnectedComponent *>> *pFrontier, std::vector<Guard *> *guards)
{
    BackendContainer::drawSurface(series);
    QImage *texture=new QImage(ncols,nrows,QImage::Format_ARGB32);

    for(int i=0;i<nrows;i++){
        for(int j=0;j<ncols;j++){
            int hValue=elevData->get(i,j);
            float interpolatedHValue=(float)(hValue-minHeight)/(float)(maxHeight-minHeight);
            QColor c=interpolateColor(interpolatedHValue);
            texture->setPixelColor(j,i,c);
        }
    }

    int hueStep = 180 / pFrontier->size();
    int saturation = 255; // Fixed saturation
    int value = 255;      // Fixed value

    std::unordered_set<int> usedGuardsIds;
    //int f=0;
    for(int f=0;f<pFrontier->size();f++){
        QColor yColor;
        int hue = f * hueStep;
        cv::Mat bgrMat;
        cv::Mat hsvMat(1, 1, CV_8UC3, cv::Scalar(hue, saturation, value));
        cv::cvtColor(hsvMat, bgrMat, cv::COLOR_HSV2BGR);
        cv::Vec3b temp=bgrMat.at<cv::Vec3b>(0,0);
        //cout<< hsvMat <<endl;
        yColor.setRed(temp.val[0]);
        yColor.setGreen(temp.val[1]);
        yColor.setBlue(temp.val[2]);

        //vSeries.at(g)->setWireframeColor(yColor);//***
        for(int ccI=0;ccI<pFrontier->at(f).size();ccI++){
            for(int ccrI=0;ccrI<pFrontier->at(f).at(ccI)->colRangeInRow.size();ccrI++){
                ConnectedRow conR = pFrontier->at(f).at(ccI)->colRangeInRow.at(ccrI);
                for(int pI=0;pI<conR.xStart.size();pI++){
                    for(int cI=conR.xStart.at(pI);cI<conR.xEnd.at(pI);cI++){
                        texture->setPixelColor(cI,conR.compRow,yColor);
                    }
                }
            }
            usedGuardsIds.insert(pFrontier->at(f).at(ccI)->owner->index);
        }
    }

    for(int g=0;g<vSeries.size() && g<guards->size();g++){
        QColor yColor;
        if (usedGuardsIds.find(guards->at(g)->index) != usedGuardsIds.end()) {
            yColor.setRed(255);
            yColor.setGreen(0);
            yColor.setBlue(0);
        } else {
            yColor.setRed(0);
            yColor.setGreen(0);
            yColor.setBlue(0);
        }
        vSeries.at(g)->setWireframeColor(yColor);

        QSurfaceDataArray *viewerData=new QSurfaceDataArray();
        int x=guards->at(g)->x;
        int z=guards->at(g)->z;
        int sH=elevData->get(x,z);
        int y=guards->at(g)->h+sH;

        QSurfaceDataRow *a=new QSurfaceDataRow();
        QSurfaceDataItem *d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x+viewerSize);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        a=new QSurfaceDataRow();
        d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        a=new QSurfaceDataRow();
        d=new QSurfaceDataItem();
        d->setX(z+viewerSize);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        d=new QSurfaceDataItem();
        d->setX(z-viewerSize);
        d->setY(y);
        d->setZ(x-viewerSize);
        a->append(*d);
        delete d;
        viewerData->append(*a);
        delete a;

        vSeries.at(g)->dataProxy()->resetArray(*viewerData);
    }
    series->setTexture(*texture);

    delete(texture);
}

void BackendContainer::removeSelection(QSurface3DSeries *series){
    //series->setSelectedPoint(series->invalidSelectionPosition());
}

/*
 * This is s simple linear interpolation betweeen multipl RGB colors with different ranges.
 */
QColor BackendContainer::interpolateColor(float in){
    QColor gc1( "darkgreen" );
    QColor gc2( "darkslategray" );
    QColor gc3( "peru" );
    QColor gc4( "white" );
    QColor colors[4]={gc1,gc2,gc3,gc4};//Gradient colors

    float vals[4]={0.0,0.15,0.7,1.0};//Gradient ranges

    int pI=0;
    int nI=0;
    float cumulativeValue=0;
    for(int i=0;i<sizeof(vals);i++){
        if(cumulativeValue>=in){
            pI=i-1;//Previous color
            nI=i;//Next color
            break;
        }
        cumulativeValue=cumulativeValue+vals[i+1];
    }
    if(pI<0){
        pI=0;
    }
    if(nI==0 && pI==0){
        return colors[0];
    }
    float internalInterpolation=(in-vals[pI])/(vals[nI]-vals[pI]);//Interpolate between two adjacent colors
    int rNew=colors[pI].red()*(1-internalInterpolation)+colors[nI].red()*internalInterpolation;
    int gNew=colors[pI].green()*(1-internalInterpolation)+colors[nI].green()*internalInterpolation;
    int bNew=colors[pI].blue()*(1-internalInterpolation)+colors[nI].blue()*internalInterpolation;

    return QColor(rNew,gNew,bNew);
}

void BackendContainer::runSingleGuardAlgFrontend(QSurface3DSeries *series, const QVariantList &vmSeries, int numGuards, int heightOffset, int radius, QString initGuardType)
{
    theSga.initializeGuards(numGuards,heightOffset,radius,elevData,initGuardType.toStdString());

    if (theSga.run(numGuards,heightOffset,radius,elevData,initGuardType.toStdString()))
    {
        std::vector<QSurface3DSeries*> vSeries;
        for(int i=0;i<vmSeries.size();i++){
            QSurface3DSeries *targetSeries = qvariant_cast<QSurface3DSeries*>(vmSeries.at(i));
            vSeries.push_back(targetSeries);
        }
        if(theSga.getFrontier()->size()>0){
            drawFrontiers(series,vSeries,theSga.getFrontier(), theSga.getGuards());
        }
        else
        {
            cout << "No solution!" << endl;
        }
    }
    //drawViewBatchSurface(series,vSeries,sga->guards,NULL);

}

void BackendContainer::drawSingleGuards(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, int numGuards, int heightOffset, int radius, QString initGuardType)
{
    theSga.initializeGuards(numGuards,heightOffset,radius,elevData,initGuardType.toStdString());
    // Need a new button
    theSga.exportForILP();
    drawViewBatchSurface(series,vSeries,theSga.getGuards(),NULL);
}

void BackendContainer::runMultiGuardAlgFrontend(QSurface3DSeries *series, const QVariantList &vmSeries, int numGuards, int heightOffset, int radius, QString initGuardType, int pairingOrder)
{
    theMga.initializeGuards(numGuards,heightOffset,radius,elevData,initGuardType.toStdString());
    theMga.mixGuardsToOrder(pairingOrder);
    std::vector<Guard *> *guards = theMga.getGuards();
    numGuards = guards->size(); // Size changes after running mixGuardsToOrder()

    if (theMga.run(numGuards,heightOffset,radius,elevData,initGuardType.toStdString(),pairingOrder))
    {
        std::vector<QSurface3DSeries*> vSeries;
        for(int i=0;i<vmSeries.size();i++){
            QSurface3DSeries *targetSeries = qvariant_cast<QSurface3DSeries*>(vmSeries.at(i));
            vSeries.push_back(targetSeries);
        }
        if(theMga.getFrontier()->size()>0){
            drawFrontiers(series,vSeries,theMga.getFrontier(),theMga.getGuards());
        }
        else
        {
            cout << "No solution!" << endl;
        }
    }
}

void BackendContainer::drawMultiGuards(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, int numGuards, int heightOffset, int radius, QString initGuardType, int pairingOrder)
{
    theMga.initializeGuards(numGuards,heightOffset,radius,elevData,initGuardType.toStdString());
    theMga.mixGuardsToOrder(pairingOrder);
    theMga.exportForILP();
    drawViewBatchSurface(series,vSeries,theMga.getGuards(),NULL);
}

/*
void BackendContainer::drawMultipleGuards(QSurface3DSeries *series, QVariantList &vmSeries,std::vector<Guard> guards){
    for(int i=0;i<5;i++){
        std::string obsX_str = std::to_string(guards.at(i).x);
        const char* obsX_p = obsX_str.c_str();
        std::string obsY_str = std::to_string(guards.at(i).z);
        const char* obsY_p = obsY_str.c_str();
        std::string obsH_str = std::to_string(guards.at(i).h);
        const char* obsH_p = obsH_str.c_str();
        std::string range_str = std::to_string(guards.at(i).r);
        const char* range_p = range_str.c_str();
        const char *options[9]={"","1201","1201",obsX_p,obsY_p,obsH_p,range_p,in_file.c_str(),"100"};

        read_delta_time();           // Initialize the timer.
        Get_Options(8, options);
        Calc_Vis();
        viewshedData=viewshedp;

        //QSurface3DSeries targetSeries = vmSeries.at(i).value<QSurface3DSeries>();
        //BackendContainer::drawViewSurface(series,&targetSeries,QString::fromStdString(obsX_str),QString::fromStdString(obsY_str),QString::fromStdString(obsH_str),QString::fromStdString(range_str),255,0,0);

    }
}
*/
