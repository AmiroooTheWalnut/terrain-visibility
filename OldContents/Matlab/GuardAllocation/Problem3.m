clc
clear
isParallel=1;
addpath('./TriangleRayIntersection')
sizeTerrain=400;
numCandidateGaurds=10;
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

numGaurds=numCandidateGaurds;
rawColors=hsv(numGaurds);
colors = rawColors(randperm(size(rawColors, 1)),:);
for i=1:numCandidateGaurds
    orig=[candidateGaurds(i),1,height];
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
        end
    end
    scatter3(generatedX,generatedY,generatedZ+i,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
    scatter3(candidateGaurds(1,i),1,height,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
end

bw(size(terrainPoints,1),size(terrainPoints,2),numCandidateGaurds)=0;
bw=logical(bw);
for i=1:numCandidateGaurds
    orig=[candidateGaurds(1,i),1,height];
    [visibleFaces,visibleVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel);
    
    for h=1:size(visibleVerticesSizes,1)
        if visibleVerticesSizes(h,1)>1
            x_h=vertices(h,2);
            y_h=vertices(h,1);
            bw(x_h,y_h,i)=1;
        end
    end
    
end

manualGraph=makeVertices(size(terrainPoints,2),numCandidateGaurds);
manualGraph=connectGraphGoodposition(manualGraph,bw);
manualGraph=connectGraphToEdge(manualGraph,bw);
%manualGraph=connectGraphGaurdToGaurd(manualGraph,bw);
%manualGraph=connectGraphWithinGaurd(manualGraph,bw);
matlabGraph=makeMatlabCompatibleGraph(manualGraph);
events = {'edgetonew'};
v = bfsearch(matlabGraph,1,events);
path=searchFromTopV(manualGraph,v,0,sizeTerrain,0,[],0,size(v,1),0);
selectedGaurds=[];
for i=1:size(path,2)
    selectedGaurds(1,size(selectedGaurds,2)+1)=manualGraph{path(1,i),1};
end
selectedGaurds=unique(selectedGaurds);

figure(2)
clf
hold on;
surf(X,Y,terrainPoints,'FaceColor','w')
daspect([1,1,1])
view([45,45])
for i=2:size(selectedGaurds,2)
    orig=[candidateGaurds(1,selectedGaurds(i)),1,height];
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
        end
    end
    scatter3(generatedX,generatedY,generatedZ+i,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
    scatter3(candidateGaurds(1,selectedGaurds(i)),1,height,'MarkerEdgeColor',colors(i,:),'MarkerFaceColor',colors(i,:))
end


disp('!')

function [path,foundEnd,endInd,foundStart]=searchFromTopV(manualGraph,v,start,targetP,targetG,path,foundEnd,endInd,foundStart)
if foundStart==1
    return;
end
if foundEnd==0
    for i=1:size(v,1)
        manualGraph{v(i,2)+1,2}
        if manualGraph{v(i,2)+1,2}==targetP
            foundEnd=1;
            endInd=i;
            path(1,size(path,2)+1)=v(i,2)+1;
            if manualGraph{v(i,1)+1,2}==start
                path(1,size(path,2)+1)=v(i,1)+1;
                foundStart=1;
                return;
            else
                [path,foundEnd,endInd,foundStart]=searchFromTopV(manualGraph,v,start,manualGraph{v(i,1)+1,2},manualGraph{v(i,1)+1,1},path,foundEnd,endInd,foundStart);
            end
        end
        if foundStart==1
            return;
        end
    end
else
    for i=endInd:-1:1
        if manualGraph{v(i,2)+1,2}==targetP && manualGraph{v(i,2)+1,1}==targetG
            endInd=i;
            path(1,size(path,2)+1)=v(i,2)+1;
            if manualGraph{v(i,1)+1,2}==start
                path(1,size(path,2)+1)=v(i,1)+1;
                foundStart=1;
                return;
            else
                [path,foundEnd,endInd,foundStart]=searchFromTopV(manualGraph,v,start,manualGraph{v(i,1)+1,2},manualGraph{v(i,1)+1,1},path,foundEnd,endInd,foundStart);
            end
        end
        if foundStart==1
            return;
        end
    end
end

end

function manualGraph=connectGraphToEdge(g,bw)
neughbors=[];
for i=1:size(bw,3)
    if bw(1,1,i)==1
        neughbors(1,size(neughbors,2)+1)=2+(i-1)*size(bw,2)+1;
    end
end
g{2,3}=neughbors;
manualGraph=g;
end

function manualGraph=connectGraphGoodposition(g,bw)
% i=1;
% k=1;
% j=20;
% m=200;
for i=1:size(bw,3)
    for k=1:size(bw,2)
        for j=1:size(bw,3)
            for m=1:size(bw,2)
                if i~=j || k~=m
%                     if i==1 && k==1 && j==5 && m==1
%                         disp('!!!!!!!')
%                     end
                    if bw(1,k,i)>0 && bw(1,m,i)>0
                        sharedVis=logical(bw(:,:,i)+bw(:,:,j));
                        if isGoodPosition(sharedVis,k,m)==1
                            sourceIndex=2+(i-1)*size(bw,2)+k;
                            destinationIndex=2+(j-1)*size(bw,2)+m;
                            sourceNeighbors=g{sourceIndex,3};
                            destinationNeighbors=g{destinationIndex,3};
                            sourceNeighbors(1,size(sourceNeighbors,2)+1)=destinationIndex;
                            destinationNeighbors(1,size(destinationNeighbors,2)+1)=sourceIndex;
                            g{sourceIndex,3}=unique(sourceNeighbors);
                            g{destinationIndex,3}=unique(destinationNeighbors);
                            %                         if sourceIndex==3 || destinationIndex==3
                            %                             if destinationIndex==4002 || sourceIndex==4002
                            %                                 disp('!!!!!!!')
                            %                             end
                            %                         end
                        end
                    end
                end
            end
        end
    end
end
manualGraph=g;
end

function matlabGraph=makeMatlabCompatibleGraph(manualGraph)
    graphMatrix(size(manualGraph,1)-1,size(manualGraph,1)-1)=0;
    for i=2:size(manualGraph,1)
        for j=1:size(manualGraph{i,3},2)
            source=i-1;
            destination=manualGraph{i,3}(1,j)-1;
            graphMatrix(source,destination)=1;
        end
    end
    for i=1:size(graphMatrix,1)
        for j=1:size(graphMatrix,2)
            if graphMatrix(i,j)==1
                graphMatrix(j,i)=1;
            end
        end
    end
    matlabGraph=graph(graphMatrix);
%     edgeMatrixSources=[];
%     edgeMatrixDestination=[];
%     for i=2:size(graph,1)
%         for j=1:size(graph{i,3},2)
%             source=i-1;
%             destination=graph{i,3}(1,j);
%             edgeMatrixSources(1,size(edgeMatrixSources,2)+1,1)=source;
%             edgeMatrixDestination(1,size(edgeMatrixDestination,2)+1,1)=destination;
%         end
%     end
%     matlabGraph=graph(edgeMatrixSources,edgeMatrixDestination);
    %disp('!')
end

function manualGraph=connectGraphWithinGaurd(g,bw)
    for i=1:size(bw,3)
        for j=1:size(bw,2)
            neighbors=g{2+(i-1)*size(bw,2)+j,3};
            for k=1:size(bw,2)
                neighborCounter=2+(i-1)*size(bw,2)+k;
                if j~=k
                    if bw(1,j,i)==1
                        if bw(1,j,i)==1
                            neighbors(1,size(neighbors,2)+1)=neighborCounter;
                        end
                    end
                end
            end
            g{2+(i-1)*size(bw,2)+j,3}=neighbors;
        end
    end
    manualGraph=g;
end

function manualGraph=connectGraphGaurdToGaurd(g,bw)
    neighbors=[];
    i=0;
    for j=1:size(bw,3)
        neighbors(1,size(neighbors,2)+1)=3+(j-1)*size(bw,2)+i;
    end
    g{2,3}=neighbors;
    for i=1:size(bw,2)
        for j=1:size(bw,3)
            neighbors=[];
            for k=1:size(bw,3)
                neighborCounter=2+(k-1)*size(bw,2)+i;
                if j~=k
                    if bw(1,i,j)==1
                        if bw(1,i,k)==1
                            neighbors(1,size(neighbors,2)+1)=neighborCounter;
                        end
                    end
                end
            end
            g{2+(j-1)*size(bw,2)+i,3}=neighbors;
        end
    end
    neighbors=[];
    i=size(bw,2);
    for j=1:size(bw,3)
        neighbors(1,size(neighbors,2)+1)=2+(j-1)*size(bw,2)+i;
    end
    g{size(g,1)+1,3}=neighbors;
    g{size(g,1),1}=inf;
    g{size(g,1),2}=inf;
    manualGraph=g;
end

function manualGraph=makeVertices(numPoints,numCandidateGaurds)
    manualGraph=cell(1,2);
    manualGraph{1,1}='Gaurd';
    manualGraph{1,2}='Point';
    manualGraph{1,3}='Neighbors';
    manualGraph{2,1}=0;
    manualGraph{2,2}=0;
    manualGraph{2,3}=[];
    counter=3;
    for i=1:numCandidateGaurds
        for j=1:numPoints
            manualGraph{counter,1}=i;
            manualGraph{counter,2}=j;
            manualGraph{counter,3}=[];
            counter=counter+1;
        end
    end
end

function result=isGoodPosition(vis,p1i,p2i)
result=1;
startI=min(p1i,p2i);
endI=max(p1i,p2i);
for i=startI:endI
    if vis(1,i)==0
        result=0;
        return;
    end
end
end