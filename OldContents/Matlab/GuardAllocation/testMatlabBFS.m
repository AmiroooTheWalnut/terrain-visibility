clc
clear
s = [1 1 1 1 2 2 2 2 2 7];
t = [3 5 4 2 6 10 7 9 8 11];
G = graph(s,t);
plot(G)
events = {'edgetofinished'};
v = bfsearch(G,2,events)