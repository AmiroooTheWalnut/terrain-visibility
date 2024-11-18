/**
 * Written by Amir Mohammad Esmaieeli Sikaroudi in November 2024.
 * This file contains the GUI components and JavaScript calls for the C++ frontend functions.
 */

import QtQuick
import QtQuick.Controls
import QtGraphs
import QtQuick.Layouts
import QtQuick3D
import BackendContainer

Window {
    property real maxHeight: 4000
    property real minHeight: -50
    property real maxX: 1201
    property real maxZ: 1201

    id: mainWindow

    width: 640
    height: 480
    visible: true
    title: qsTr("Visibility GUI")

    BackendContainer {
        id: backendContainer
    }

    TextField {
        width: 200
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.horizontalCenterOffset: 1
        id: elevDataNameTextField
        text: qsTr("tiles/N32W110.hgt")
    }

    Button {
        anchors.top: elevDataNameTextField.bottom
        anchors.left: parent.left
        anchors.horizontalCenterOffset: 1

        id: getElevDataButton
        text: qsTr("Get data")
        onClicked: getElevData()

        function getElevData(){
            backendContainer.readElevData(elevDataNameTextField.text);
        }
    }

    Button {
        anchors.top: elevDataNameTextField.bottom
        anchors.left: getElevDataButton.right
        anchors.horizontalCenterOffset: 1

        id: drawButton
        text: qsTr("Draw map")
        onClicked: drawMap()

        function drawMap(){
            var ret=backendContainer.drawSurface(heightSeries);
            maxHeight=Number(ret[0]);
            minHeight=Number(ret[1]);
            maxX=Number(ret[2]);
            maxZ=Number(ret[3]);
        }
    }

    Label {
        id: obsXLabel
        anchors.top: parent.top
        anchors.left: elevDataNameTextField.right
        text: "Obs X: "
        color: "black"
    }

    TextField {
        width: 50
        anchors.top: parent.top
        anchors.left: obsXLabel.right
        anchors.horizontalCenterOffset: 1
        id: obsXTextField
        text: qsTr("50")
    }

    Label {
        id: obsZLabel
        anchors.top: parent.top
        anchors.left: obsXTextField.right
        text: "Obs Z: "
        color: "black"
    }

    TextField {
        width: 50
        anchors.top: parent.top
        anchors.left: obsZLabel.right
        anchors.horizontalCenterOffset: 1
        id: obsZTextField
        text: qsTr("50")
    }

    Label {
        id: obsHLabel
        anchors.top: parent.top
        anchors.left: obsZTextField.right
        text: "Obs H: "
        color: "black"
    }

    TextField {
        width: 50
        anchors.top: parent.top
        anchors.left: obsHLabel.right
        anchors.horizontalCenterOffset: 1
        id: obsHTextField
        text: qsTr("5")
    }

    Label {
        id: obsRLabel
        anchors.top: parent.top
        anchors.left: obsHTextField.right
        text: "Obs R: "
        color: "black"
    }

    TextField {
        width: 50
        anchors.top: parent.top
        anchors.left: obsRLabel.right
        anchors.horizontalCenterOffset: 1
        id: obsRTextField
        text: qsTr("20")
    }

    Button {
        anchors.top: elevDataNameTextField.bottom
        anchors.left: obsXLabel.left
        anchors.horizontalCenterOffset: 1

        id: drawViewButton
        text: qsTr("Draw view map")
        onClicked: drawViewMap()

        function drawViewMap(){
            var ret=backendContainer.drawViewSurface(heightSeries,viewerSeries,obsXTextField.text,obsZTextField.text,obsHTextField.text,obsRTextField.text);
        }
    }

    Item {
        id: surfaceView
        anchors.top: getElevDataButton.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        Gradient {
            id: surfaceGradient
            GradientStop { position: 0.0; color: "darkgreen"}
            GradientStop { position: 0.15; color: "darkslategray" }
            GradientStop { position: 0.7; color: "peru" }
            GradientStop { position: 1.0; color: "white" }
        }

        Surface3D {
            id: surfacePlot
            width: surfaceView.width
            height: surfaceView.height
            aspectRatio: 3.0
            theme: GraphsTheme {
                colorScheme: GraphsTheme.ColorScheme.Dark
                labelFont.family: "STCaiyun"
                labelFont.pointSize: 35
                colorStyle: GraphsTheme.ColorStyle.ObjectGradient
                baseGradients: [surfaceGradient] // Use the custom gradient
                //baseColors: ["#FFFF0000"]
            }
            shadowQuality: Graphs3D.ShadowQuality.Medium
            selectionMode: Graphs3D.SelectionFlag.Item
            //selectionMode: Graphs3D.SelectionFlag.Slice | Graphs3D.SelectionFlag.ItemAndRow

            cameraPreset: Graphs3D.CameraPreset.IsometricLeft

            axisX.min: -0.01
            axisY.min: mainWindow.minHeight
            axisZ.min: -0.01
            axisX.max: mainWindow.maxX
            axisY.max: mainWindow.maxHeight
            axisZ.max: mainWindow.maxZ
            axisX.segmentCount: 4
            axisY.segmentCount: 4
            axisZ.segmentCount: 4

            axisY.title: "Height (m)"
            axisX.title: "Longitude (m)"
            axisZ.title: "Latitude (m)"
            axisY.titleVisible: true
            axisX.titleVisible: true
            axisZ.titleVisible: true

            //! [0]
            Surface3DSeries {
                id: heightSeries
                shading: Surface3DSeries.Shading.Smooth
                drawMode: Surface3DSeries.DrawSurface

                // Heightmap can be used for debugging

                // HeightMapSurfaceDataProxy {
                //     heightMapFile: "://temp.png"
                //     autoScaleY: true
                //     minYValue: 800
                //     maxYValue: 5000
                //     minZValue: -1
                //     maxZValue: 1201
                //     minXValue: -1
                //     maxXValue: 1201
                // }

                onSelectedPointChanged: {
                    obsXTextField.text=heightSeries.selectedPoint.y;
                    obsZTextField.text=heightSeries.selectedPoint.x;
                }
            }

            Surface3DSeries {
                id: viewerSeries
                //shading: Surface3DSeries.Shading.Smooth
                drawMode: Surface3DSeries.DrawWireframe

            }
        }


    }


}
