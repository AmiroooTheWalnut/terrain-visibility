cmake_minimum_required(VERSION 3.16)

project(VP VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

#find_package(Qt6 6.5 REQUIRED COMPONENTS Quick)
find_package(Qt6 COMPONENTS Core)
find_package(Qt6 COMPONENTS Gui)
find_package(Qt6 COMPONENTS Qml)
find_package(Qt6 COMPONENTS Quick)
find_package(Qt6 COMPONENTS Quick3D)
find_package(Qt6 COMPONENTS Graphs)
#find_package(Qt6 COMPONENTS DataVisualization)
find_package(OpenCV REQUIRED)

qt_standard_project_setup(REQUIRES 6.5)

qt_add_executable(appVP
    frontend/main.cpp
)


if(WIN32)
    qt_add_qml_module(appVP
        URI VP
        VERSION 1.0
        NO_RESOURCE_TARGET_PATH
        QML_FILES frontend/Main.qml
        SOURCES  backend/tiledMatrix.cpp backend/TiledVS.cpp
        RESOURCES tiles/N32W110.hgt
        RESOURCES heightmap.png
        RESOURCES temp.png
        SOURCES backend/TiledVS.h
        SOURCES backend/tiledMatrix.h
        SOURCES backend/lz4.cpp
        SOURCES backend/lz4.h
        SOURCES BackendContainer.cpp
        SOURCES BackendContainer.h
	
	SOURCES backend/guard.h backend/guard.cpp
    	SOURCES backend/connectedcomponent.h backend/connectedcomponent.cpp
    	SOURCES backend/multiguardalgorithm.h backend/multiguardalgorithm.cpp
    	SOURCES backend/singleguardalgorithm.h backend/singleguardalgorithm.cpp
    	QML_FILES frontend/surface_template.qml

        SOURCES sys/times.h
        SOURCES sys/times.c
        SOURCES sys/uio.h

    )

elseif(UNIX)

    qt_add_qml_module(appVP
        URI VP
        VERSION 1.0
        NO_RESOURCE_TARGET_PATH
        QML_FILES frontend/Main.qml
        SOURCES  backend/tiledMatrix.cpp backend/TiledVS.cpp
        RESOURCES tiles/N32W110.hgt
        RESOURCES heightmap.png
        RESOURCES temp.png
        SOURCES backend/TiledVS.h
        SOURCES backend/tiledMatrix.h
        SOURCES backend/lz4.cpp
        SOURCES backend/lz4.h
        SOURCES BackendContainer.cpp
        SOURCES BackendContainer.h

	SOURCES backend/guard.h backend/guard.cpp
    	SOURCES backend/connectedcomponent.h backend/connectedcomponent.cpp
    	SOURCES backend/multiguardalgorithm.h backend/multiguardalgorithm.cpp
    	SOURCES backend/singleguardalgorithm.h backend/singleguardalgorithm.cpp
    	QML_FILES frontend/surface_template.qml
    )

endif()


# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
set_target_properties(appVP PROPERTIES
#    MACOSX_BUNDLE_GUI_IDENTIFIER com.example.appVP
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

target_link_libraries(appVP PUBLIC
    Qt::Core
    Qt::Gui
    Qt::Quick
    Qt::Qml
    Qt::Quick3D
    Qt::Graphs
    #Qt::DataVisualization
    ${OpenCV_LIBS}
)

include(GNUInstallDirs)
install(TARGETS appVP
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# Define source and destination directories
set(SOURCE_FOLDER "${CMAKE_SOURCE_DIR}/tiles")
set(DEST_FOLDER "${CMAKE_BINARY_DIR}/tiles")

include_directories(${OpenCV_INCLUDE_DIRS})

#target_include_directories(${PROJECT_NAME} PUBLIC
#    "${CMAKE_SOURCE_DIR}/backend")
#add_subdirectory("${CMAKE_SOURCE_DIR}/backend")
#include_directory(include)
#target_include_directories(appVP PUBLIC "${CMAKE_SOURCE_DIR}/backend")

# Add a custom target to copy the folder
add_custom_target(CopyResources ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${SOURCE_FOLDER} ${DEST_FOLDER}
    COMMENT "Copying resources folder to build directory"
)

# Ensure the copy happens before the executable runs
add_dependencies(appVP CopyResources)
