% ==============================
% A* 算法求解罗马尼亚地图最短路径
% 起点：Arad   终点：Bucharest
% ==============================
clear; clc;

%% 1. 定义地图（邻接表：城市名 + 邻居 + 距离）
cities = {
    'Arad','Zerind','Oradea','Sibiu','Timisoara',...
    'Lugoj','Mehadia','Drobeta','Craiova','Rimnicu Vilcea',...
    'Fagaras','Pitesti','Bucharest','Giurgiu','Urziceni',...
    'Vaslui','Iasi','Neamt','Hirsova','Eforie'
};

% 邻接表：graph{i} 存放 [邻居编号, 距离]
graph = cell(length(cities),1);
graph{1}  = [2 75; 4 140; 5 118];        % Arad
graph{2}  = [1 75; 3 71];                 % Zerind
graph{3}  = [2 71; 4 151];               % Oradea
graph{4}  = [1 140; 3 151; 11 99; 10 80]; % Sibiu
graph{5}  = [1 118; 6 111];               % Timisoara
graph{6}  = [5 111; 7 70];                % Lugoj
graph{7}  = [6 70; 8 75];                 % Mehadia
graph{8}  = [7 75; 9 120];                % Drobeta
graph{9}  = [8 120; 10 146; 12 138];      % Craiova
graph{10} = [4 80; 9 146; 12 97];         % Rimnicu Vilcea
graph{11} = [4 99; 13 211];               % Fagaras
graph{12} = [10 97; 9 138; 13 101];       % Pitesti
graph{13} = [11 211; 12 101; 14 90; 15 85];% Bucharest
graph{14} = [13 90];                      % Giurgiu
graph{15} = [13 85; 16 142; 17 98];       % Urziceni
graph{16} = [15 142; 17 92];              % Vaslui
graph{17} = [16 92; 18 87];               % Iasi
graph{18} = [17 87];                      % Neamt
graph{19} = [15 98; 20 86];               % Hirsova
graph{20} = [19 86];                      % Eforie

%% 2. 启发函数 h(n)：到 Bucharest(13) 的直线距离
heuristic = [
    366, 374, 380, 253, 329, ...
    244, 241, 242, 160, 193, ...
    178, 98, 0, 77, 80, ...
    199, 226, 234, 151, 161
];

%% 3. A* 算法主体
start = 1;    % Arad
goal  = 13;   % Bucharest

n = length(cities);
g = inf(1, n); g(start) = 0;    % 实际代价
f = inf(1, n); f(start) = heuristic(start); % f = g + h
came_from = zeros(1, n);         % 父节点
closed = false(1, n);           % 已访问

while true
    % 找 f 最小且未被访问的节点
    candidates = f;
    candidates(closed) = inf;
    [~, current] = min(candidates);
    
    if current == goal || isinf(f(current))
        break;
    end
    
    closed(current) = true;
    
    % 遍历邻居
    neighbors = graph{current};
    for i = 1:size(neighbors,1)
        neighbor = neighbors(i,1);
        cost     = neighbors(i,2);
        if closed(neighbor)
            continue;
        end
        tentative_g = g(current) + cost;
        if tentative_g < g(neighbor)
            came_from(neighbor) = current;
            g(neighbor) = tentative_g;
            f(neighbor) = g(neighbor) + heuristic(neighbor);
        end
    end
end

%% 4. 回溯路径
path = [];
c = goal;
while c ~= 0
    path = [c, path];
    c = came_from(c);
end

%% 5. 输出结果
fprintf('最短路径：\n');
for i = 1:length(path)
    fprintf('%s', cities{path(i)});
    if i < length(path)
        fprintf(' → ');
    end
end
fprintf('\n总距离：%d km\n', g(goal));