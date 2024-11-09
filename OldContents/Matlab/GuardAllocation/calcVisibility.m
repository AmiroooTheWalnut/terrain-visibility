function [finalFaces,finalVerticesSizes] = calcVisibility(orig,vertices,faces,X,Y,terrainPoints,isParallel)
%CALCVISIBILITY Summary of this function goes here
%   Detailed explanation goes here
visibleVertices(size(vertices,1),1)=0;
spz = interp2(X,Y,terrainPoints, orig(1,1),orig(1,2));
if orig(1,3)>spz
    if isParallel==0
        for i=1:size(vertices,1)
            dir   = [-orig(1,1)+vertices(i,1)+0.0001+(rand(1,1))*0.0001 -orig(1,2)+vertices(i,2)+0.0001+(rand(1,1))*0.0001 -orig(1,3)+vertices(i,3)+0.001];
            
            vert1 = vertices(faces(:,1),:);
            vert2 = vertices(faces(:,2),:);
            vert3 = vertices(faces(:,3),:);
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
        parfor i=1:size(vertices,1)
            dir   = [-orig(1,1)+vertices(i,1)+0.0001+(rand(1,1))*0.0001 -orig(1,2)+vertices(i,2)+0.0001+(rand(1,1))*0.0001 -orig(1,3)+vertices(i,3)+0.1];
            
            vert1 = vertices(faces(:,1),:);
            vert2 = vertices(faces(:,2),:);
            vert3 = vertices(faces(:,3),:);
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
end

finalFaces(size(faces,1),1)=0;
finalVerticesSizes=0.001*ones(size(vertices,1),1);

for i=1:size(visibleVertices,1)
    if visibleVertices(i,1)==1
        finalVerticesSizes(i,1)=40;
    end
end

for i=1:size(faces,1)
    if visibleVertices(faces(i,1),1)==1 && visibleVertices(faces(i,2),1)==1 && visibleVertices(faces(i,3),1)==1
        finalFaces(i)=1;
    end
end
end

