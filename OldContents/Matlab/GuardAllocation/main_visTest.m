clc
clear
global isParallel;
isParallel=1;
addpath('./TriangleRayIntersection')
figure(1)
clf
sizeTerrain=60;

[X,Y] = meshgrid(1:sizeTerrain,1:sizeTerrain);

faces = delaunay(X,Y);

%\/\/\/ PEAKS CASE STUDY
% terrainPoints = peaks(sizeTerrain);
%^^^ PEAKS CASE STUDY

%\/\/\/ AMIR'S CASE STUDY
rng(56)
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
%^^^ AMIR'S CASE STUDY

if isParallel==1
    p = gcp('nocreate');
    if isempty(p)
        parpool;
    end
end

figure(1);
clf;
vertices = [X(:) Y(:) terrainPoints(:)];

handle.a = axes;

handle.p = trisurf(faces, X,Y,terrainPoints,'EdgeColor','none');
handle.x = reshape(X,1,[]);
handle.y = reshape(Y,1,[]);
handle.z = reshape(terrainPoints,1,[]);
handle.X=X;
handle.Y=Y;
handle.Z=terrainPoints;
handle.vertices=vertices;
handle.faces=faces;
handle.p.ButtonDownFcn = {@click,handle};

daspect([1,1,1])

% makeVisibilityPlot(handle,[19,21,terrainPoints(19,21)+0.01])

function click(obj,eventData,handle)
orig=getOrig(handle);
if orig==-1
    return;
end
orig(1,3)=orig(1,3)+0.05;

makeVisibilityPlot(handle,orig);
end

function makeVisibilityPlot(handle,orig)
global isParallel;
tic

visibleVertices(size(handle.vertices,1),1)=0;
if isParallel==0
    for i=1:size(handle.vertices,1)
        dir   = [-orig(1,1)+handle.vertices(i,1)+0.0001+(rand(1,1))*0.0001 -orig(1,2)+handle.vertices(i,2)+0.0001+(rand(1,1))*0.0001 -orig(1,3)+handle.vertices(i,3)+0.1];
        
        vert1 = handle.vertices(handle.faces(:,1),:);
        vert2 = handle.vertices(handle.faces(:,2),:);
        vert3 = handle.vertices(handle.faces(:,3),:);
        %     tic;
        [intersect, t, u, v, xcoor] = TriangleRayIntersection(orig, dir, vert1, vert2, vert3, 'planetype', 'one sided', 'lineType', 'segment');
%         if handle.vertices(i,1)==19 && handle.vertices(i,2)==45
%                     fprintf('Number of: faces=%i, points=%i, intresections=%i; time=%f sec\n', ...
%                         size(handle.faces,1), size(handle.vertices,1), sum(intersect), toc);
%         
%         
%                     figure(5); clf;
%                     trisurf(handle.faces,handle.X,handle.Y,handle.Z, intersect*1.0,'FaceAlpha', 0.9)
%                     hold on;
%                     line('XData',orig(1)+[0 dir(1)],'YData',orig(2)+[0 dir(2)],'ZData',...
%                         orig(3)+[0 dir(3)],'Color','r','LineWidth',3)
%                     set(gca, 'CameraPosition', [106.2478  -35.9079  136.4875])
%                     %set(gco,'EdgeColor','none');
%                     disp('!!!')
%         end
        if sum(intersect)==0
            visibleVertices(i,1)=1;
        end
    end
else
    parfor i=1:size(handle.vertices,1)
        dir   = [-orig(1,1)+handle.vertices(i,1)+0.0001+(rand(1,1))*0.0001 -orig(1,2)+handle.vertices(i,2)+0.0001+(rand(1,1))*0.0001 -orig(1,3)+handle.vertices(i,3)+0.1];
        
        vert1 = handle.vertices(handle.faces(:,1),:);
        vert2 = handle.vertices(handle.faces(:,2),:);
        vert3 = handle.vertices(handle.faces(:,3),:);
        %     tic;
        [intersect, t, u, v, xcoor] = TriangleRayIntersection(orig, dir, vert1, vert2, vert3, 'planetype', 'one sided', 'lineType', 'segment');
        %             fprintf('Number of: faces=%i, points=%i, intresections=%i; time=%f sec\n', ...
        %                 size(handle.faces,1), size(handle.vertices,1), sum(intersect), toc);
        %
        %
        %             figure(5); clf;
        %             trisurf(handle.faces,handle.X,handle.Y,handle.Z, intersect*1.0,'FaceAlpha', 0.9)
        %             hold on;
        %             line('XData',orig(1)+[0 dir(1)],'YData',orig(2)+[0 dir(2)],'ZData',...
        %                 orig(3)+[0 dir(3)],'Color','r','LineWidth',3)
        %             set(gca, 'CameraPosition', [106.2478  -35.9079  136.4875])
        %             %set(gco,'EdgeColor','none');
        if sum(intersect)==0
            visibleVertices(i,1)=1;
        end
    end
end

finalFaces(size(handle.faces,1),1)=0;

finalVerticesSizes=0.001*ones(size(handle.vertices,1),1);

for i=1:size(visibleVertices,1)
    if visibleVertices(i,1)==1
        finalVerticesSizes(i,1)=40;
    end
end

for i=1:size(handle.faces,1)
    if visibleVertices(handle.faces(i,1),1)==1 && visibleVertices(handle.faces(i,2),1)==1 && visibleVertices(handle.faces(i,3),1)==1
        finalFaces(i)=1;
    end
end

figure(2);
cla;
trisurf(handle.faces, handle.X,handle.Y,handle.Z, finalFaces,'FaceAlpha', 0.9,'LineWidth',0.01);
%set(gco,'EdgeColor','none');
hold on;
scatter3(handle.vertices(:,1),handle.vertices(:,2),handle.vertices(:,3), finalVerticesSizes, 'filled', 'MarkerFaceColor',[1 0 0])
scatter3(orig(1,1),orig(1,2),orig(1,3),60,'filled', 'MarkerFaceColor',[0 1 1]);

daspect([1,1,1])
elapsedTime = toc;
disp('Elapsed time: ')
disp(elapsedTime)
end

function [selectedPoint]=getOrig(handle)
selectedPoint=-1;
Pt = handle.a.CurrentPoint(1,:);
Pt2 = handle.a.CurrentPoint(2,:);
orig=Pt;

dir = [-orig(1,1)+Pt2(1,1) -orig(1,2)+Pt2(1,2) -orig(1,3)+Pt2(1,3)+0.1];

vert1 = handle.vertices(handle.faces(:,1),:);
vert2 = handle.vertices(handle.faces(:,2),:);
vert3 = handle.vertices(handle.faces(:,3),:);
[intersect, t, u, v, xcoor] = TriangleRayIntersection(orig, dir, vert1, vert2, vert3, 'planetype', 'two sided', 'lineType', 'segment');
minDist=inf;
selectedFace=-1;
for i=1:size(intersect,1)
    if intersect(i,1)==1
        if t(i,1)<minDist
            minDist=t(i,1);
            selectedFace=i;
        end
    end
end
if selectedFace>-1
    ps(3,3)=0;
    ps(1,:)=handle.vertices(handle.faces(selectedFace,1),:);
    ps(2,:)=handle.vertices(handle.faces(selectedFace,2),:);
    ps(3,:)=handle.vertices(handle.faces(selectedFace,3),:);
    ds(1,3)=0;
    arr = [ps(1,:);xcoor(selectedFace,:)];
    ds(1,1) = pdist(arr,'euclidean');
    arr = [ps(2,:);xcoor(selectedFace,:)];
    ds(1,2) = pdist(arr,'euclidean');
    arr = [ps(3,:);xcoor(selectedFace,:)];
    ds(1,3) = pdist(arr,'euclidean');
    [~,I]=min(ds);
    selectedPoint=ps(I,:);
end

end
