clc
clear
n=20;
[x,y] = meshgrid(1:n,1:n);    % create 2D mesh of points
faces = delaunay(x,y);        % triangulate it using Delaunay algorithm
z     = peaks(n);             % sample function defined on a grid of the same dimenision
vertices = [x(:) y(:) z(:)];  % vertices stored as Nx3 matrix
orig  = [9 9 z(9,9)+0.1];         % ray's origin

visibleVertices(size(vertices,1),1)=0;

for i=1:size(vertices,1)
    dir   = [-orig(1,1)+vertices(i,1) -orig(1,2)+vertices(i,2) -orig(1,3)+vertices(i,3)+0.1];         % ray's direction
    vert1 = vertices(faces(:,1),:);
    vert2 = vertices(faces(:,2),:);
    vert3 = vertices(faces(:,3),:);
    tic;
    [intersect, t, u, v, xcoor] = TriangleRayIntersection(orig, dir, vert1, vert2, vert3, 'planetype', 'one sided', 'lineType', 'segment');
    fprintf('Number of: faces=%i, points=%i, intresections=%i; time=%f sec\n', ...
        size(faces,1), size(vertices,1), sum(intersect), toc);
    
    
    figure(5); clf;
    trisurf(faces,x,y,z, intersect*1.0,'FaceAlpha', 0.9)
    hold on;
    line('XData',orig(1)+[0 dir(1)],'YData',orig(2)+[0 dir(2)],'ZData',...
        orig(3)+[0 dir(3)],'Color','r','LineWidth',3)
    set(gca, 'CameraPosition', [106.2478  -35.9079  136.4875])
    %set(gco,'EdgeColor','none');
    if sum(intersect)==0
        visibleVertices(i,1)=1;
    end
end

finalFaces(size(faces,1),1)=0;

counter=1;
for i=1:size(visibleVertices,1)
    if visibleVertices(i,1)==1
        finalVertices(counter,1)=vertices(i,1);
        finalVertices(counter,2)=vertices(i,2);
        finalVertices(counter,3)=vertices(i,3);
        counter=counter+1;
    end
end

for i=1:size(faces,1)
    if visibleVertices(faces(i,1),1)==1 && visibleVertices(faces(i,2),1)==1 && visibleVertices(faces(i,3),1)==1
        finalFaces(i)=1;
    end
end

figure(5); clf;
trisurf(faces,x,y,z, finalFaces,'FaceAlpha', 0.9)
hold on;
scatter3(finalVertices(:,1),finalVertices(:,2),finalVertices(:,3),'filled', 'MarkerFaceColor',[1 0 0])
scatter3(orig(1,1),orig(1,2),orig(1,3),50,'filled', 'MarkerFaceColor',[0 1 1]);
set(gca, 'CameraPosition', [106.2478  -35.9079  136.4875])
%set(gco,'EdgeColor','none');

daspect([1,1,1])
