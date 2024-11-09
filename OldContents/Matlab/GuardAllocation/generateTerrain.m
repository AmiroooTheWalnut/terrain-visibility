function [terrainPoints,faces,vertices,X,Y] = generateTerrain(sizeTerrain)
%GENERATETERRAIN Summary of this function goes here
%   Detailed explanation goes here
[X,Y] = meshgrid(1:sizeTerrain,1:sizeTerrain);
faces = delaunay(X,Y);
rng(123)
terrainPoints(sizeTerrain,sizeTerrain)=0;
numSins=4+round(rand(1,1)*10);

for k=1:numSins
    freqs(k)=3+rand(1,1)*5;
    heights(k)=0.1+rand(1,1)*2;
    mul1(k)=-0.5+rand(1,1)*2;
    mul2(k)=-0.5+rand(1,1)*2;
end

for i=1:sizeTerrain
    for j=1:sizeTerrain
        for k=1:numSins
            terrainPoints(X(i,j),Y(i,j))=terrainPoints(X(i,j),Y(i,j))+sin((mul1(k)*X(i,j)+mul2(k)*Y(i,j))/freqs(k))*heights(k);
        end
    end
end
vertices = [X(:) Y(:) terrainPoints(:)];
end

