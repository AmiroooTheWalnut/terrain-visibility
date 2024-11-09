clc
clear
isParallel=1;
addpath('./TriangleRayIntersection')
sizeTerrain=400;
numCandidateGaurds=20;
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
pi_v=cell(size(terrainPoints,1),size(terrainPoints,2));
for i=2:sizeTerrain
    d(1,i)=inf;
    d(2,i)=inf;
end
isOtherSizeReached=0;
for f=1:3
    for j=1:1
        for i=1:numCandidateGaurds
            for k=1:numCandidateGaurds
                if i~=k
                    bw=[];
                    bw(size(terrainPoints,1),size(terrainPoints,2))=0;
                    bw=logical(bw);
                    orig=[candidateGaurds(1,i),1,height];
                    [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
                    
                    for h=1:size(visibleVerticesSizes,1)
                        if visibleVerticesSizes(h,1)>1
                            x_h=vertices(h,2);
                            y_h=vertices(h,1);
                            bw(x_h,y_h)=1;
                        end
                    end
                    
                    orig=[candidateGaurds(1,k),1,height];
                    [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
                    
                    for h=1:size(visibleVerticesSizes,1)
                        if visibleVerticesSizes(h,1)>1
                            x_h=vertices(h,2);
                            y_h=vertices(h,1);
                            bw(x_h,y_h)=1;
                        end
                    end
                    CC = bwconncomp(bw);
%                     if i==1 && k==11
%                         disp('!!!')
%                     end
%                     if i==1 && k==16
%                         disp('!!!')
%                     end
                    for o=1:size(CC.PixelIdxList,2)
                        minVal=getMinInPatch(CC.PixelIdxList{1,o},d,terrainPoints);
                        patch=CC.PixelIdxList{1,o};
                        for m=1:size(patch,1)
                            
                            yp=floor((patch(m,1)+1)/size(terrainPoints,1));
                            xp=mod(patch(m,1)+1,2)+1;
                            if d(xp,yp)>minVal+1
                                d(xp,yp)=minVal+1;
                                pi_v{xp,yp}=[i,k];
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
                end
            end
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
selectedGaurds=cell(1,0);
currentD=0;
for i=1:size(d,2)
    if d(1,i)>currentD
        currentD=d(1,i);
        isBroken=0;
        for j=1:size(d,2)
            if d(1,j)>currentD
                selectedGaurds{1,size(selectedGaurds,2)+1}=pi_v{1,j-1};
                isBroken=1;
                break;
            end
        end
        if isBroken==0
            selectedGaurds{1,size(selectedGaurds,2)+1}=pi_v{1,j};
        end
%         if currentD<d(1,i)
%             selectedGaurds{1,size(selectedGaurds,2)+1}=pi_v{1,i-1};
%         end
    end
end

numGaurds=size(selectedGaurds,2);
rawColors=hsv(numGaurds);
colors = rawColors(randperm(size(rawColors, 1)),:);

for i=1:numGaurds
    
        orig=[candidateGaurds(1,selectedGaurds{1,i}(1,1)),1,height];
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
        scatter3(candidateGaurds(1,selectedGaurds{1,i}(1,1)),1,height,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
        
        orig=[candidateGaurds(1,selectedGaurds{1,i}(1,2)),1,height];
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
        scatter3(candidateGaurds(1,selectedGaurds{1,i}(1,2)),1,height+i,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
        
        minHeight=min(min(terrainPoints));
        for k=1:size(d,2)
            if d(1,k)>0
                scatter3(k,1,minHeight-5,'MarkerEdgeColor',colors(d(1,k),:),'MarkerFaceColor',colors(d(1,k),:))
            end
        end
end

%colorsSegments = rawColors(randperm(max(max(d))),:);


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