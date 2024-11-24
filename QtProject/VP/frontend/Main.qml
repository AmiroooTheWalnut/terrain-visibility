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

    property var surfComponent;
    property var sufaceQMLItem;

    property var lastCamera;
    property var cameraPresent;
    property var cameraTargetPosition;
    property var cameraXRotation;
    property var cameraYRotation;
    property var cameraZoomLevel;

    property var axisX;
    property var axisY;
    property var axisZ;

    id: mainWindow

    width: 1150
    height: 788
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
            if (typeof sufaceQMLItem !== "undefined") {
                axisX=sufaceQMLItem.children[0].axisX;
                axisY=sufaceQMLItem.children[0].axisY;
                axisZ=sufaceQMLItem.children[0].axisZ;
                //lastCamera=sufaceQMLItem.children[0].camera;
                //cameraPresent=sufaceQMLItem.children[0].cameraPresent;
                cameraTargetPosition=sufaceQMLItem.children[0].cameraTargetPosition;
                cameraXRotation=sufaceQMLItem.children[0].cameraXRotation;
                cameraYRotation=sufaceQMLItem.children[0].cameraYRotation;
                cameraZoomLevel=sufaceQMLItem.children[0].cameraZoomLevel;

                sufaceQMLItem.destroy();
            }
            surfComponent = Qt.createComponent("surface_template.qml");

            if (surfComponent.status == Component.Ready){
                    finishCreation();
            }else{
                surfComponent.statusChanged.connect(finishCreation);
            }
        }

        function finishCreation() {
            if (surfComponent.status == Component.Ready) {
                sufaceQMLItem = surfComponent.createObject(mainWindow);
                if (sufaceQMLItem == null) {
                    // Error Handling
                    console.log("Error creating object");
                }
                if(typeof cameraTargetPosition!=="undefined"){
                    //sufaceQMLItem.children[0].camera=lastCamera;
                    //sufaceQMLItem.children[0].cameraPresent=cameraPresent;

                    sufaceQMLItem.children[0].axisX=axisX;
                    sufaceQMLItem.children[0].axisY=axisY;
                    sufaceQMLItem.children[0].axisZ=axisZ;

                    sufaceQMLItem.children[0].cameraTargetPosition=cameraTargetPosition;
                    sufaceQMLItem.children[0].cameraXRotation=cameraXRotation;
                    sufaceQMLItem.children[0].cameraYRotation=cameraYRotation;
                    sufaceQMLItem.children[0].cameraZoomLevel=cameraZoomLevel;
                }

                // var ret=backendContainer.drawSurface(heightSeries);
                var ret=backendContainer.drawSurface(sufaceQMLItem.children[0].seriesList[0]);
                maxHeight=Number(ret[0]);
                minHeight=Number(ret[1]);
                maxX=Number(ret[2]);
                maxZ=Number(ret[3]);
            } else if (surfComponent.status == Component.Error) {
                // Error Handling
                console.log("Error loading component:", component.errorString());
            }
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
            if (typeof sufaceQMLItem !== "undefined") {
                axisX=sufaceQMLItem.children[0].axisX;
                axisY=sufaceQMLItem.children[0].axisY;
                axisZ=sufaceQMLItem.children[0].axisZ;

                cameraTargetPosition=sufaceQMLItem.children[0].cameraTargetPosition;
                cameraXRotation=sufaceQMLItem.children[0].cameraXRotation;
                cameraYRotation=sufaceQMLItem.children[0].cameraYRotation;
                cameraZoomLevel=sufaceQMLItem.children[0].cameraZoomLevel;
                sufaceQMLItem.destroy();
            }
            surfComponent = Qt.createComponent("surface_template.qml");

            if (surfComponent.status == Component.Ready){
                    finishCreation();
            }else{
                surfComponent.statusChanged.connect(finishCreation);
            }
        }

        function finishCreation() {
            if (surfComponent.status == Component.Ready) {
                sufaceQMLItem = surfComponent.createObject(mainWindow);
                if (sufaceQMLItem == null) {
                    // Error Handling
                    console.log("Error creating object");
                }
                if(typeof cameraTargetPosition!=="undefined"){
                    //sufaceQMLItem.children[0].camera=lastCamera;
                    //sufaceQMLItem.children[0].cameraPresent=cameraPresent;

                    sufaceQMLItem.children[0].axisX=axisX;
                    sufaceQMLItem.children[0].axisY=axisY;
                    sufaceQMLItem.children[0].axisZ=axisZ;

                    sufaceQMLItem.children[0].cameraTargetPosition=cameraTargetPosition;
                    sufaceQMLItem.children[0].cameraXRotation=cameraXRotation;
                    sufaceQMLItem.children[0].cameraYRotation=cameraYRotation;
                    sufaceQMLItem.children[0].cameraZoomLevel=cameraZoomLevel;
                }
                // var ret=backendContainer.drawSurface(heightSeries);
                //var ret=backendContainer.drawViewSurface(sufaceQMLItem.children[0].seriesList[0],sufaceQMLItem.children[0].seriesList[1],obsXTextField.text,obsZTextField.text,obsHTextField.text,obsRTextField.text,255,255,0);
                var ret=dispatchDrawViewRequest(sufaceQMLItem.children[0].seriesList[0],sufaceQMLItem.children[0].seriesList[1],obsXTextField.text,obsZTextField.text,obsHTextField.text,obsRTextField.text,255,255,0);
            } else if (surfComponent.status == Component.Error) {
                // Error Handling
                console.log("Error loading component:", component.errorString());
            }
        }

        function dispatchDrawViewRequest(surfSeries,viewerSeries,x,z,h,range,red,green,blue){
            var ret=backendContainer.drawViewSurface(surfSeries,viewerSeries,x,z,h,range,red,green,blue);
            return ret;
        }
    }

    Item {
        id: algorithmsPanel
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 200
        anchors.right: parent.right

        Label {
            id: sgaNGLabel
            anchors.top: parent.top
            anchors.left: parent.left
            text: "Number of guards: "
            color: "black"
        }

        TextField {
            width: 50
            anchors.top: sgaNGLabel.bottom
            anchors.left: parent.left
            anchors.horizontalCenterOffset: 1
            id: sgaNGTextField
            text: qsTr("10")
        }

        Button {
            anchors.top: sgaNGTextField.bottom
            anchors.left: parent.left
            anchors.horizontalCenterOffset: 1
            id: singleGuardAlgButton
            text: qsTr("Single Guard Algorithm")
            onClicked: singleGuardAlg()

            property var viewersSeriesObject;
            function singleGuardAlg(){
                if (typeof sufaceQMLItem !== "undefined") {
                    drawButton.drawMap();
                }

                var header=`import QtQuick
                import QtGraphs
                `;
                var contentTemplate1=`Surface3DSeries {
                objectName: "`;
                var contentTemplate2=`"
                drawMode: Surface3DSeries.DrawWireframe
                itemLabelVisible: false
                }
                `;
                var contentTrunk=header;
                var numGuards=parseInt(sgaNGTextField.text);
                for(let i=0;i<numGuards;i++){
                    contentTrunk=contentTrunk+contentTemplate1+"viewerSeries"+i+contentTemplate2;
                }

                viewersSeriesObject = Qt.createQmlObject(contentTrunk,algorithmsPanel);


                if (viewersSeriesObject.status == Component.Ready){
                        finishCreation();
                }else{
                    viewersSeriesObject.statusChanged.connect(finishCreation);
                }
            }

            function finishCreation() {
                if (viewersSeriesObject.status == Component.Ready) {
                    var viewerList = viewersSeriesObject.createObject(sufaceQMLItem);
                    if (viewerList == null) {
                        // Error Handling
                        console.log("Error creating object");
                    }
                    backendContainer.runSingleGuardAlgFrontend(sufaceQMLItem.children[0].seriesList[0]);
                    //dispatchDrawViewRequest(sufaceQMLItem.children[0].seriesList[0],sufaceQMLItem.children[0].seriesList[1],obsXTextField.text,obsZTextField.text,obsHTextField.text,obsRTextField.text,255,255,0);
                } else if (viewersSeriesObject.status == Component.Error) {
                    // Error Handling
                    console.log("Error loading component:", component.errorString());
                }
            }
        }
    }

}
