/**
 * Written by Amir Mohammad Esmaieeli Sikaroudi in November 2024.
 * This file connects the backend and frontend. This file is not put inside frontend folder because of compiler errors.
 * The functions for drawing the elevation map and viewshed are provided.
 */

#ifndef BACKENDCONTAINER_H
#define BACKENDCONTAINER_H

#include <QObject>
#include "backend/TiledVS.h"
#include "backend/guard.h"
#include <QtGraphs/qsurface3dseries.h>
//#include <QtGraphs/qsurface3d.h>
#include <QtQml/qqmlregistration.h>

class BackendContainer : public QObject
{
    Q_OBJECT
    QML_ELEMENT

public:
    explicit BackendContainer(QObject *parent = nullptr);
    const float viewerSize=5;
    tiledMatrix<elev_t>* elevData;
    tiledMatrix<unsigned char>* viewshedData;
    Q_INVOKABLE void readElevData(const QString file_name);
    void updateVisibility(QString obsX, QString obsY, QString obsH,QString range);
    Q_INVOKABLE QList<QString> drawSurface(QSurface3DSeries *series);
    Q_INVOKABLE QList<QString> drawViewSurface(QSurface3DSeries *series, QSurface3DSeries *vSeries, const QString obsX, const QString obsY, const QString obsH, const QString range, int r,int g,int b);
    void drawViewBatchSurface(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, std::vector<Guard> guards, std::vector<QColor> *explicitColors);
    Q_INVOKABLE void drawSingleGuards(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, int numGuards, int heightOffset, int radius, QString initGuardType);
    Q_INVOKABLE void drawMultiGuards(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, int numGuards, int heightOffset, int radius, QString initGuardType, int pairingOrder);
    void drawFrontiers(QSurface3DSeries *series, std::vector<QSurface3DSeries*> vSeries, std::vector<std::vector<ConnectedComponent *>> *pFrontier, std::vector<Guard> *guards);
    QColor interpolateColor(float in);
    Q_INVOKABLE void removeSelection(QSurface3DSeries *series);
    Q_INVOKABLE void runSingleGuardAlgFrontend(QSurface3DSeries *series, const QVariantList &vmSeries, int numGuards, int heightOffset, int radius, QString initGuardType);
    Q_INVOKABLE void runMultiGuardAlgFrontend(QSurface3DSeries *series, const QVariantList &vmSeries, int numGuards, int heightOffset, int radius, QString initGuardType, int pairingOrder);
    //void drawMultipleGuards(QSurface3DSeries *series, QVariantList &vmSeries,std::vector<Guard> guards);

    QSurfaceDataArray *viewerData=new QSurfaceDataArray();
    QSurfaceDataArray *surfaceData=new QSurfaceDataArray();
};


#endif // BACKENDCONTAINER_H
