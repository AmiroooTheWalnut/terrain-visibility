clc
clear
isParallel=1;
addpath('./TriangleRayIntersection')
sizeTerrain=200;
numCandidateGaurds=20;
bestSolution=[];
height=80;
%[terrainPoints,faces,vertices,X,Y]=generate2DTerrain(sizeTerrain);
[terrainPoints,faces,vertices,X,Y]=generate2DStepTerrain(sizeTerrain);
if isParallel==1
    p = gcp('nocreate');
    if isempty(p)
        parpool;
    end
end
%\/\/\/ TEST
% orig=[10,10,terrainPoints(10,10)];
% [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,isParallel);
% figure(1);
% cla;
% trisurf(faces,X,Y,terrainPoints,visibleFaces,'FaceAlpha',0.9,'LineWidth',0.01);
%^^^ TEST
figure(1)
clf
hold on;
surf(X,Y,terrainPoints,'FaceColor','w')
daspect([1,1,1])
view([45,45])
%trisurf(faces,X,Y,terrainPoints);
%daspect([1,1,1])
candidateGaurds = linspace(1,sizeTerrain,numCandidateGaurds);

d(size(terrainPoints,1),size(terrainPoints,2))=0;
pi_v(size(terrainPoints,1),size(terrainPoints,2))=0;
for i=2:sizeTerrain
    d(1,i)=inf;
    d(2,i)=inf;
end
isOtherSizeReached=0;
for f=1:10
    for j=1:1
        for i=1:numCandidateGaurds
            bw=[];
            orig=[candidateGaurds(1,i),1,height];
            [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
            %             trisurf(faces,X,Y,terrainPoints,visibleFaces,'FaceAlpha',0.9,'LineWidth',0.01);
            %             hold on;
            %             scatter3(vertices(:,1),vertices(:,2),vertices(:,3), visibleVerticesSizes, 'filled', 'MarkerFaceColor',[1 0 0])
            %             scatter3(orig(1,1),orig(1,2),orig(1,3),60,'filled', 'MarkerFaceColor',[0 1 1]);
            %             daspect([1,1,1])
            %disp('1')
            bw(size(terrainPoints,1),size(terrainPoints,2))=0;
            bw=logical(bw);
            for h=1:size(visibleVerticesSizes,1)
                if visibleVerticesSizes(h,1)>1
                    x_h=vertices(h,2);
                    y_h=vertices(h,1);
                    bw(x_h,y_h)=1;
                end
            end
%             figure(2)
%             imagesc(bw)
            CC = bwconncomp(bw);
            for o=1:size(CC.PixelIdxList,2)
                minVal=getMinInPatch(CC.PixelIdxList{1,o},d,terrainPoints);
                patch=CC.PixelIdxList{1,o};
                for m=1:size(patch,1)
                    yp=floor((patch(m,1)+1)/size(terrainPoints,1));
                    xp=mod(patch(m,1)+1,2)+1;
                    if d(xp,yp)>minVal+1
                        d(xp,yp)=minVal+1;
                        pi_v(xp,yp)=i;
%                         if yp==sizeTerrain
%                             isOtherSizeReached=1;
%                             disp('FOUND')
%                             break;
%                         end
                    end
                end
%                 if isOtherSizeReached==1
%                     break;
%                 end
            end
            %disp('2')
%             if isOtherSizeReached==1
%                 break;
%             end
        end
%         if isOtherSizeReached==1
%             break;
%         end
    end
%     if isOtherSizeReached==1
%         break;
%     end
end

drawSolution(vertices,faces,X,Y,terrainPoints,d,pi_v,candidateGaurds,height,isParallel);

function drawSolution(vertices,faces,X,Y,terrainPoints,d,pi_v,candidateGaurds,height,isParallel)
selectedGaurds=unique(pi_v);

numGaurds=size(selectedGaurds,1);
rawColors=hsv(numGaurds);
colors = rawColors(randperm(size(rawColors, 1)),:);

for i=1:numGaurds
    if selectedGaurds(i,1)~=0
        orig=[candidateGaurds(1,selectedGaurds(i,1)),1,height];
        [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
        generatedX=[];
        generatedY=[];
        generatedZ=[];
        for h=1:size(visibleVerticesSizes,1)
            if visibleVerticesSizes(h,1)>1
                x_h=vertices(h,2);
                y_h=vertices(h,1);
                %bw(x_h,y_h)=1;
                generatedX(1,size(generatedX,2)+1)=X(x_h,y_h);
                generatedY(1,size(generatedY,2)+1)=Y(x_h,y_h);
                generatedZ(1,size(generatedZ,2)+1)=terrainPoints(x_h,y_h);
                %             generatedX(1,size(generatedX,2)+1)=X(2,h);
                %             generatedY(1,size(generatedY,2)+1)=Y(1,h);
                %             generatedY(1,size(generatedY,2)+1)=Y(2,h);
                %             generatedZ(1,size(generatedZ,2)+1)=terrainPoints(1,h);
                %             generatedZ(1,size(generatedZ,2)+1)=terrainPoints(2,h);
            end
        end
        scatter3(generatedX,generatedY,generatedZ+i,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
        scatter3(candidateGaurds(1,selectedGaurds(i,1)),1,height,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
    end
end

%colorsSegments = rawColors(randperm(max(max(d))),:);
minHeight=min(min(terrainPoints));
for i=1:size(d,2)
    if d(1,i)>0
        scatter3(i,1,minHeight-5,'MarkerEdgeColor',colors(d(1,i)+1,:),'MarkerFaceColor',colors(d(1,i)+1,:))
    end
end

view([45,45])
end

function minValue=getMinInPatch(patch,d,terrainPoints)
minValue=inf;
for m=1:size(patch,1)
    yp=floor((patch(m,1)+1)/size(terrainPoints,1));
    xp=mod(patch(m,1)+1,2)+1;
    if d(xp,yp)<minValue
        minValue=d(xp,yp);
    end
end
end