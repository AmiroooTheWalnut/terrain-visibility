#include <QGuiApplication>
#include <QQmlApplicationEngine>
//#ifdef QMAKE_BUILD
#include "BackendContainer.h"
//#endif
//#include "BackendContainer.h"


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
    engine.loadFromModule("VP", "Main2");

    return app.exec();
}
