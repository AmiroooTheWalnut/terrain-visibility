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
#include <opencv2/opencv.hpp>
#include<opencv2/core/mat.hpp>
#include "backend/singleguardalgorithm.h"
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
void BackendContainer::readElevData(const QString file_name){
    std::string file_name_str = file_name.toStdString();
    const char* file_name_p = file_name_str.c_str();
    const char *options[9]={"","1201","1201","50","50","10","10",file_name_p,"100"};

    // run(8,options);
    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);
    Read_Elev();
    elevData = elevp;
}

/*
 * This function calls the backend to calculate visibility and keeps a pointer to the results.
 * The size of the surface is fixed for now.
 */
void BackendContainer::updateVisibility(QString obsX, QString obsY, QString obsH, QString range){
    std::string obsX_str = obsX.toStdString();
    const char* obsX_p = obsX_str.c_str();
    std::string obsY_str = obsY.toStdString();
    const char* obsY_p = obsY_str.c_str();
    std::string obsH_str = obsH.toStdString();
    const char* obsH_p = obsH_str.c_str();
    std::string range_str = range.toStdString();
    const char* range_p = range_str.c_str();
    const char *options[9]={"","1201","1201",obsX_p,obsY_p,obsH_p,range_p,in_file.c_str(),"100"};

    read_delta_time();           // Initialize the timer.
    Get_Options(8, options);
    Calc_Vis();

    viewshedData=viewshedp;
}

/*
 * This function prepares the surface points and updates QSurface3DSeries and adds texture manually to the surface. The function returns some strings to be used in QML.
 * The size of the surface is returned.
*/
QList<QString> BackendContainer::drawSurface(QSurface3DSeries *series)
{
    QImage *texture=new QImage(nrows,ncols,QImage::Format_ARGB32);

    if(!surfaceData->isEmpty()){
        surfaceData->clear();
    }

    //QSurfaceDataArray *m_resetArray=new QSurfaceDataArray();
    for(int i=0;i<ncols;i++){
        QSurfaceDataRow *a=new QSurfaceDataRow();
        for(int j=0;j<nrows;j++){
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
    QImage *texture=new QImage(nrows,ncols,QImage::Format_ARGB32);
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
    return qList;
}

void BackendContainer::drawViewBatchSurface(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, std::vector<Guard> guards){
    BackendContainer::drawSurface(series);

    int r=255;
    int g=0;
    int b=0;

    QImage *texture=new QImage(nrows,ncols,QImage::Format_ARGB32);

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

    for(int g=0;g<vSeries.size();g++){
        int hue = g * hueStep;
        cv::Mat bgrMat;
        cv::Mat hsvMat(1, 1, CV_8UC3, cv::Scalar(hue, saturation, value));
        cv::cvtColor(hsvMat, bgrMat, cv::COLOR_HSV2BGR);
        cv::Vec3b temp=hsvMat.at<cv::Vec3b>(0,0);
        //cout<< hsvMat <<endl;
        QColor yColor(temp.val[0],temp.val[1],temp.val[2]);
        vSeries.at(g)->setWireframeColor(yColor);
        QString obsX=QString::fromStdString(std::to_string(guards.at(g).x));
        QString obsZ=QString::fromStdString(std::to_string(guards.at(g).z));
        QString obsH=QString::fromStdString(std::to_string(guards.at(g).h));
        QString range=QString::fromStdString(std::to_string(guards.at(g).r));
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

void BackendContainer::runSingleGuardAlgFrontend(QSurface3DSeries *series, const QVariantList &vmSeries, int numGuards){
    SingleGuardAlgorithm *sga=new SingleGuardAlgorithm();
    sga->run(numGuards,50,elevData);
    std::vector<QSurface3DSeries*> vSeries;
    for(int i=0;i<vmSeries.size();i++){
        QSurface3DSeries *targetSeries = qvariant_cast<QSurface3DSeries*>(vmSeries.at(i));
        vSeries.push_back(targetSeries);
    }
    drawViewBatchSurface(series,vSeries,sga->guards);
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
