import QtQuick
import QtGraphs


Item {
    id: surfaceView
    objectName: "surfaceView"
    anchors.top: getElevDataButton.bottom
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    anchors.right: optionsItem.left

    Gradient {
        id: surfaceGradient
        GradientStop { position: 0.0; color: "darkgreen"}
        GradientStop { position: 0.15; color: "darkslategray" }
        GradientStop { position: 0.7; color: "peru" }
        GradientStop { position: 1.0; color: "white" }
    }

    Surface3D {
        id: surfacePlot
        objectName: "surfacePlot"
        //renderMode: Abstract3DGraph.RenderModeOffscreen

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
        shadowQuality: Graphs3D.ShadowQuality.None
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
            objectName: "heightSeries"
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
            objectName: "viewerSeries"
            //shading: Surface3DSeries.Shading.Smooth
            drawMode: Surface3DSeries.DrawWireframe
            itemLabelVisible: false
        }


        //onSelectedSeriesChanged: {
        //            if (surfacePlot.selectedSeries === viewerSeries) {
                        // Reset selection for series2
                        //surfacePlot.selectedSeries.clearSelection();
                        //return;
        //                backendContainer.removeSelection(surfacePlot.selectedSeries);
        //            }
        //        }
    }
}
