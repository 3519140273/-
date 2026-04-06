# -
一些代码尝试
A * 算法求解罗马尼亚地图最短路径（MATLAB 实现）
项目简介
基于 A * 启发式搜索算法，实现罗马尼亚地图从 Arad 到 Bucharest 的最短路径求解。
文件说明
astar_romania.m：A * 算法主程序
运行环境
MATLAB R2016b 及以上版本
运行方法
将文件放入 MATLAB 当前工作目录
打开astar_romania.m，点击运行
命令行窗口查看路径与总距离
算法原理
A * 算法核心公式：f(n) = g(n) + h(n)
g(n)：起点到当前节点的实际代价
h(n)：当前节点到终点的直线距离（启发函数）
每次选择f(n)最小的节点扩展，保证最优路径
结果：
最短路径：Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest
总距离：418 km
