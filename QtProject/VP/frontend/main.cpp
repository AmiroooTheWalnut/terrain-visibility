/**
 * Written by Amir Mohammad Esmaieeli Sikaroudi in November 2024.
 * This file is the main file that the GUI starts with running the QML engine.
 */

#include <QGuiApplication>
#include <QQmlApplicationEngine>
//#ifdef QMAKE_BUILD
#include "BackendContainer.h"
//#endif


int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

//#ifdef QMAKE_BUILD
    qmlRegisterType<BackendContainer>("BackendContainer", 1, 0, "BackendContainer");
//#endif


// #ifdef Q_OS_WIN
//     QString extraImportPath(QStringLiteral("%1/../../../../%2"));
// #else
//     QString extraImportPath(QStringLiteral("%1/../../../%2"));
// #endif

    QQmlApplicationEngine engine;
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    engine.loadFromModule("VP", "Main");

    return app.exec();
}
