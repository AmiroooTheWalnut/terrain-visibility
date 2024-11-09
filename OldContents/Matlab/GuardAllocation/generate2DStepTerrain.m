function [terrainPoints,faces,vertices,X,Y] = generate2DStepTerrain(sizeTerrain)
[X,Y] = meshgrid(1:sizeTerrain,1:2);
faces = delaunay(X,Y);
terrainPoints(2,sizeTerrain)=0;
rng(123)
segmentSizeAvg=8+round(rand(1,1)*10);
segmentSizeStd=8+round(rand(1,1)*10);
type='dentFloor';
isActive=false;
offset=[];
segmentPassed=0;
counter=0;
for i=1:sizeTerrain
    if isActive==false
        disp(type)
        switch type
            case 'dentFloor'
                segmentLength=floor(segmentSizeAvg+(rand(1,1)*segmentSizeStd));
                if isempty(offset)==1
                    offset=rand(1,1);
                else
                    offset=terrainPoints(1,X(1,i-1));
                end
                slope=(rand(1,1)-0.5)*0.1;
            case 'dentTop'
                segmentLength=floor(segmentSizeAvg+(rand(1,1)*segmentSizeStd));
                offset=terrainPoints(1,X(1,i-1));
                slope=(rand(1,1)-0.5)*0.1;
            case 'dentDown'
                segmentLength=floor((segmentSizeAvg+(rand(1,1)*segmentSizeStd))/4);
                offset=terrainPoints(1,X(1,i-1));
                slope=-2-rand(1,1)*5;
            case 'dentUp'
                segmentLength=floor((segmentSizeAvg+(rand(1,1)*segmentSizeStd))/4);
                offset=terrainPoints(1,X(1,i-1));
                slope=2+rand(1,1)*5;
            otherwise
                disp('other value')
        end
        isActive=true;
    end
    terrainPoints(1,X(1,i))=offset+slope*counter;
    terrainPoints(2,X(2,i))=offset+slope*counter;
    counter=counter+1;
    segmentPassed=segmentPassed+1;
    if segmentPassed>segmentLength
        isActive=false;
        segmentPassed=0;
        counter=0;
        switch type
            case 'dentFloor'
                type='dentUp';
            case 'dentTop'
                type='dentDown';
            case 'dentDown'
                type='dentFloor';
            case 'dentUp'
                type='dentTop';
            otherwise
                disp('other value')
        end
    end
end
vertices = [X(:) Y(:) terrainPoints(:)];
end

