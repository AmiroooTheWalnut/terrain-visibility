/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import java.util.Random;

/**
 *
 * @author user
 */
public class TerrainGenerator {

    public static Terrain generateStepTerrain1D(int seed, int sizeTerrainX) {
        Terrain terrain = new Terrain();
        Random generator = new Random(seed);
        double[][][] XY = meshgrid(0,sizeTerrainX,0,2);
//faces = delaunay(X,Y);
        terrain.terrainPoints = new double[2][sizeTerrainX];

        double segmentSizeAvg = 8 + Math.round(generator.nextDouble() * 10.0);
        double segmentSizeStd = 8 + Math.round(generator.nextDouble() * 10.0);
        String type = "dentFloor";
        boolean isActive = false;
        double offset = -1;
        int segmentPassed = 0;
        int counter = 0;
        double segmentLength = 0;
        double slope = 0;
        for (int i = 0; i < sizeTerrainX; i++) {
            if (isActive == false) {
                System.out.println(type);
                switch (type) {
                    case "dentFloor":
                        segmentLength = Math.floor(segmentSizeAvg + (generator.nextDouble() * segmentSizeStd));
                        if (offset == -1) {
                            offset = generator.nextDouble();
                        } else {
                            offset = terrain.terrainPoints[0][(int)XY[i - 1][0][0]];
                        }
                        slope = (generator.nextDouble() - 0.5) * 0.1;
                        break;
                    case "dentTop":
                        segmentLength = Math.floor(segmentSizeAvg + (generator.nextDouble() * segmentSizeStd));
                        offset = terrain.terrainPoints[0][(int)XY[i - 1][0][0]];
                        slope = (generator.nextDouble() - 0.5) * 0.1;
                        break;
                    case "dentDown":
                        segmentLength = Math.floor((segmentSizeAvg + (generator.nextDouble() * segmentSizeStd)) / 4);
                        offset = terrain.terrainPoints[0][(int)XY[i - 1][0][0]];
                        slope = -2 - generator.nextDouble() * 5;
                        break;
                    case "dentUp":
                        segmentLength = Math.floor((segmentSizeAvg + (generator.nextDouble() * segmentSizeStd)) / 4);
                        offset = terrain.terrainPoints[0][(int)XY[i - 1][0][0]];
                        slope = 2 + generator.nextDouble() * 5;
                        break;
                    default:
                        System.out.println("other value");
                }
                isActive = true;
            }
            terrain.terrainPoints[0][(int)XY[i][0][0]] = offset + slope * counter;
            terrain.terrainPoints[1][(int)XY[i][1][0]] = offset + slope * counter;
            counter = counter + 1;
            segmentPassed = segmentPassed + 1;
            if (segmentPassed > segmentLength) {
                isActive = false;
                segmentPassed = 0;
                counter = 0;
                switch (type) {
                    case "dentFloor":
                        type = "dentUp";
                        break;
                    case "dentTop":
                        type = "dentDown";
                        break;
                    case "dentDown":
                        type = "dentFloor";
                        break;
                    case "dentUp":
                        type = "dentTop";
                        break;
                    default:
                        System.out.println("other value");
                }
            }
        }
        return terrain;
    }

    public static double[][][] meshgrid(int minX, int maxX, int minY, int maxY) {
        double[][][] output = new double[maxX - minX][maxY - minY][2];
        for (int i = minX; i < maxX-minX; i++) {
            for (int j = minY; j < maxY-minY; j++) {
                output[i][j][0] = i;
                output[i][j][1] = j;
            }
        }
        return output;
    }

}
