clc
clear
figure(1)
clf
sizeTerrain=20;
terrainPoints(sizeTerrain,sizeTerrain)=0;

[X,Y] = meshgrid(1:sizeTerrain,1:sizeTerrain);

faces = delaunay(X,Y);

terrainPoints = peaks(sizeTerrain);

% rng(56)
% 
% numSins=4+round(rand(1,1)*10);
% 
% for k=1:numSins
%     freqs(k)=3+rand(1,1)*5;
%     heights(k)=0.1+rand(1,1)*2;
%     mul1(k)=-0.5+rand(1,1)*2;
%     mul2(k)=-0.5+rand(1,1)*2;
% end
% 
% for i=1:sizeTerrain
%     for j=1:sizeTerrain
%         for k=1:numSins
%             terrainPoints(X(i,j),Y(i,j))=terrainPoints(X(i,j),Y(i,j))+sin((mul1(k)*X(i,j)+mul2(k)*Y(i,j))/freqs(k))*heights(k);
%             %terrainPoints(X(i,j),Y(i,j))=sin((-X(i,j)+Y(i,j))/3);
%         end
%     end
% end

vertices = [X(:) Y(:) terrainPoints(:)];

handle.a = axes;

handle.p = trisurf(faces, X,Y,terrainPoints);

handle.x = reshape(X,1,[]);
handle.y = reshape(Y,1,[]);
handle.z = reshape(terrainPoints,1,[]);

handle.X=X;
handle.Y=Y;
handle.Z=terrainPoints;

handle.vertices=vertices;
handle.faces=faces;

daspect([1,1,1])


handle.p.ButtonDownFcn = {@click,handle};
% definition of click
function click(obj,eventData,handle)
% co-ordinates of the current selected point
Pt = handle.a.CurrentPoint(1,:);
Pt2 = handle.a.CurrentPoint(2,:);
disp(handle.a.CurrentPoint(1,:))
disp(handle.a.CurrentPoint(2,:))
% find point closest to selected point on the plot
% for k = 1:size(handle.x,2)
%     arr = [handle.x(k) handle.y(k) handle.z(k);Pt];
%     distArr(k) = pdist(arr,'euclidean');
% end
% [~,idx] = min(distArr);
% display the selected point on plot
%disp([round(Pt(1,1)) round(Pt(1,2)) handle.Z(round(Pt(1,2)),round(Pt(1,1)))]);
orig=Pt;

visibleVertices(size(handle.vertices,1),1)=0;

dir   = [-orig(1,1)+Pt2(1,1) -orig(1,2)+Pt2(1,2) -orig(1,3)+Pt2(1,3)+0.1]; 
            
    vert1 = handle.vertices(handle.faces(:,1),:);
    vert2 = handle.vertices(handle.faces(:,2),:);
    vert3 = handle.vertices(handle.faces(:,3),:);
    tic;
    [intersect, t, u, v, xcoor] = TriangleRayIntersection(orig, dir, vert1, vert2, vert3, 'planetype', 'two sided', 'lineType', 'segment');
            fprintf('Number of: faces=%i, points=%i, intresections=%i; time=%f sec\n', ...
                size(handle.faces,1), size(handle.vertices,1), sum(intersect), toc);
    
    
            figure(5); clf;
            trisurf(handle.faces,handle.X,handle.Y,handle.Z, intersect*1.0,'FaceAlpha', 0.9)
            hold on;
            line('XData',orig(1)+[0 dir(1)],'YData',orig(2)+[0 dir(2)],'ZData',...
                orig(3)+[0 dir(3)],'Color','r','LineWidth',3)
            set(gca, 'CameraPosition', [106.2478  -35.9079  136.4875])
            %set(gco,'EdgeColor','none');
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
            scatter3(selectedPoint(1,1),selectedPoint(1,2),selectedPoint(1,3),60,'filled', 'MarkerFaceColor',[0 1 1]);
            disp('!!!!!!!!!!!!!!')

end

% roi = images.roi.Cuboid(gca,'Color','r');
% draw(roi)
