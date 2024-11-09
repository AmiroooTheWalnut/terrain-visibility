clc
clear
isParallel=0;
addpath('./TriangleRayIntersection')
tic
sizeTerrain=240;
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
figure(1)
clf
hold on;
surf(X,Y,terrainPoints,'FaceColor','w')
daspect([1,1,1])
view([45,45])
candidateGaurds = linspace(1,sizeTerrain,numCandidateGaurds);

levels=cell(1,1);
levels{1,1}=cell(1,numCandidateGaurds);
C = nchoosek(1:numCandidateGaurds,2);
for i=1:size(C,1)
    levels{1,1}{1,i}=C(i,:);
end
currentLevel=1;
for i=1:size(levels{currentLevel,1},2)
    if hasPathToEnd(candidateGaurds,levels{currentLevel,1}{1,i},height,vertices,faces,X,Y,terrainPoints,isParallel)==true
        bestSolution=levels{currentLevel,1}{1,i};
    end
    if isConnectedToStart(candidateGaurds,levels{currentLevel,1}{1,i},height,vertices,faces,X,Y,terrainPoints,isParallel)==true
        levels=branchNextLevel(levels,currentLevel,i,numCandidateGaurds);
    end
end
isSolFound=false;
while size(levels{currentLevel,1},2)>0
    currentLevel=currentLevel+1;
    for i=1:size(levels{currentLevel,1},2)
        if hasPathToEnd(candidateGaurds,levels{currentLevel,1}{1,i},height,vertices,faces,X,Y,terrainPoints,isParallel)==true
            hasPathToEnd(candidateGaurds,levels{currentLevel,1}{1,i},height,vertices,faces,X,Y,terrainPoints,isParallel);
            bestSolution=levels{currentLevel,1}{1,i};
            isSolFound=true;
            break;
        else
            levels=branchNextLevel(levels,currentLevel,i,numCandidateGaurds);
        end
    end
    if isSolFound==true
        break;
    end
end

drawSolution(vertices,faces,X,Y,terrainPoints,bestSolution,candidateGaurds,height,isParallel);

elapsed=toc;
disp(elapsed)

function levels=branchNextLevel(levels,currentLevel,currentNode,numCandidateGaurds)
start=max(levels{currentLevel,1}{1,currentNode})+1;
if size(levels,1)<currentLevel+1
    levels{currentLevel+1,1}=cell(0,0);
end
if size(start:numCandidateGaurds,2)<1
    return;
end
counter=size(levels{currentLevel+1,1},2);
candidates=[];
for i=1:numCandidateGaurds
    iFoundInSet=false;
    for j=1:size(levels{currentLevel,1}{1,currentNode},2)
        if i==levels{currentLevel,1}{1,currentNode}(1,j)
            iFoundInSet=true;
            break;
        end
    end
    if iFoundInSet==false
        candidates(1,size(candidates,2)+1)=i;
    end
end
C = nchoosek(candidates,2);
for i=1:size(C,1)
    previousSol=levels{currentLevel,1}{1,currentNode};
    levels{currentLevel+1,1}{1,counter+1}=[previousSol,C(i,1),C(i,2)];
    counter=counter+1;
end
end

function [pathFound]=hasPathToEnd(gaurdCandidates,gaurdIndices,height,vertices,faces,X,Y,terrainPoints,isParallel)
bw(size(terrainPoints,1),size(terrainPoints,2))=0;
bw=logical(bw);
for i=1:size(gaurdIndices,2)
    orig=[gaurdCandidates(gaurdIndices(1,i)),1,height];
    [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
    for h=1:size(visibleVerticesSizes,1)
        if visibleVerticesSizes(h,1)>1
            x_h=vertices(h,2);
            y_h=vertices(h,1);
            bw(x_h,y_h)=1;
        end
    end
end
for i=1:size(bw,2)
    if bw(1,i)==0
        pathFound=false;
        return;
    end
end
pathFound=true;
end

function [connected]=isConnectedToStart(gaurdCandidates,gaurdIndices,height,vertices,faces,X,Y,terrainPoints,isParallel)
bw(size(terrainPoints,1),size(terrainPoints,2))=0;
bw=logical(bw);
for i=1:size(gaurdIndices,2)
    orig=[gaurdCandidates(gaurdIndices(1,i)),1,height];
    [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
    for h=1:size(visibleVerticesSizes,1)
        if visibleVerticesSizes(h,1)>1
            x_h=vertices(h,2);
            y_h=vertices(h,1);
            bw(x_h,y_h)=1;
        end
    end
end
if bw(1,1)==0
    connected=false;
    return;
else
    connected=true;
end
end

function drawSolution(vertices,faces,X,Y,terrainPoints,bestSolution,gaurdCandidates,height,isParallel)
numGaurds=size(bestSolution,2);
rawColors=hsv(numGaurds);
colors = rawColors(randperm(size(rawColors, 1)),:);

%bw(size(terrainPoints,1),size(terrainPoints,2))=0;
%bw=logical(bw);
for i=1:size(bestSolution,2)
    orig=[gaurdCandidates(bestSolution(1,i)),1,height];
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
    scatter3(gaurdCandidates(1,bestSolution(1,i)),1,height,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
end
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
