function [terrainPoints,faces,vertices,X,Y] = generate2DTerrain(sizeTerrain)
[X,Y] = meshgrid(1:sizeTerrain,1:2);
faces = delaunay(X,Y);
rng(123)
terrainPoints(2,sizeTerrain)=0;
numSins=4+round(rand(1,1)*10);

for k=1:numSins
    freqs(k)=3+rand(1,1)*5;
    heights(k)=0.1+rand(1,1)*2;
    mul1(k)=-0.5+rand(1,1)*2;
    mul2(k)=-0.5+rand(1,1)*2;
end

for i=1:sizeTerrain
    for k=1:numSins
        terrainPoints(1,X(1,i))=terrainPoints(1,X(1,i))+sin((mul1(k)*X(1,i)+mul2(k)*Y(1,i))/freqs(k))*heights(k);
        terrainPoints(2,X(2,i))=terrainPoints(2,X(2,i))+sin((mul1(k)*X(1,i)+mul2(k)*Y(1,i))/freqs(k))*heights(k);
    end
end
vertices = [X(:) Y(:) terrainPoints(:)];
end

