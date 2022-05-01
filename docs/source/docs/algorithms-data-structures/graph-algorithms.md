# Graph Algorithms

Code snippets of few basic ones.

## Bipartite Graph

No adjacent same color.

Thus no odd-number-edge cycles.

## Basic Search

* Depth First Search (DFS): Stack
* Breadth First Search (BFS): Queue

| Problem                                             | Algorithm |
| --------------------------------------------------- | --------- |
| DFS/BFS Tree                                        | DFS/BFS   |
| DFS/BFS Tree (Disconnected)                         | DFS/BFS   |
| Connectivity                                        | DFS/BFS   |
| Cycle in Undirected Graph                           | DFS/BFS   |
| Cycle in Directed Graph                             | DFS       |
| Reachability of Vertices                            | DFS/BFS   |
| Shortest Distance of Vertices                       | BFS       |
| Diameter                                            | BFS       |
| Eulerian Tour                                       | DFS       |
| Topological Sort                                    | DFS       |
| Sinks and Sources of DAG                            | DFS       |
| Connected Component                                 | DFS       |
| Biconnected Component, Strongly Connected Component | DFS       |

## Shortest Path

### Bellman-Ford

The algorithm works if no negative cycles exist, but can detect such cycle otherwise

Run (n-1) rounds to update shortest path from source node

```cpp
vector<int> dist = vector<int>(n+1,INF);
dist[s] = 0;
for(int i = 0; i < n-1; ++i) {
  for(auto e:edges) {
    // a: start node, b: end node, w: weight
    int a = e->a, b = e->b, w = e->w;
    dist[b] = min(dist[b], dist[a] + w);
  }
}
```

If there is still a change in the last iteration, there exists a negative cycle.

```cpp
vector<int> dist = vector<int>(n+1,INF);
vector<int> parent = vector<int>(n, -1);
dist[s] = 0;
int c = -1;
// execute the loop n times, using the last iteration to test
for(int i = 0; i < n; ++i) {
  for(auto e:edges) {
    // a: start node, b: end node, w: weight
    int a = e->a, b = e->b, w = e->w;
    if (dist[a] + w < dist[b]) {
      dist[b] = dist[a] + w;
      parent[b] = a;
      if (i == n-1) cycle = b;
    }
  }
}

if (c == -1) return; // no cycle

// go backward to enter the cycle
for (int i = 0; i < n; ++i) c = parent[c];

// find the nodes on the cycle
vector<int> cycle;
int x = c;
while(x != c || cycle.empty()) {
  cycle.push_back(x);
  x = parent[x];
}
// reverse to parent->child order
reverse(cycle.begin(), cycle.end());

// cycle stores the nodes on the negative cycle
```

### Dijkstra's

aka Best First Search

It's just a graph search using priority queue.

For C++, can multiply the distance by `-1` to use the min_heap (std::priority_queue<> default) as a max_heap.

```cpp
x->dist = 0;

pq.push(make_pair(-x->dist,x));

while (!pq.empty()) {
  auto t = pq.top(); pq.pop();
  Node* n = t.second;
  int d = -t.first;
  if (!n->done) {
    n->done = 1;
    for (auto ne : n->neighbors) {
      if (n->dist + d < ne->dist) {
        ne->prev = n;
        ne->dist = n->dist + d;
        pq.push(make_pair(-ne->dist, ne));
      }
    }
  }
}
```

The algorithm requires that no edge has negative weight.
Because it assumes that using additional edge will always
increase the total length.

### Floyd-Warshall

Find shortest path from anywhere to anywhere.

Use an adjacency matrix. Store results in a distance matrix.

Select a node and try to reduce dist using this node.

Initialize distance matrix:

```cpp
for(int i = 1; i <= n; ++i) {
  for(int j = 1; j <= n; ++j) {
    if(i == j) dist[i][j] = 0;
    else if(adj[i][j]) dist[i][j] = adj[i][j];
    else dist[i][j] = INF;
  }
}
```

Find:

```cpp
for (int k = 1; k <= n; ++k) {
  for (int i = 1; i <=n; ++i) {
    for (int j = 1; j <=n; ++j) {
      dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
    }
  }
}
```

## Union Find

N elements, each element has index $i \in [0,N-1]$.

Union: connect two elements so that `uf[i]` of one points to another

* doesn't matter which one
* usually use the smaller index for the union, `uf[j] = i` when `j > i`

Find: find element belongs to which union, represented by the smallest index of the elements

Connected: check if two elements in the same union

* just check if the find(), i.e. "top" index of the two unions, are the same

```cpp
vector<int> uf(N);
// each element is their own union initially
for (int i = 0; i < N; ++i) uf[i] = i;

// chase the "pointers"
int find(int i) {
  while (i != uf[i]) i = uf[i];
  return i;
}

bool connected(int i, int j) {
  return find(i) == find(j);
}

void union(int i, int j) {
  i = find(i);
  j = find(j);
  uf[i] = uf[j] = min(i, j);
}
```

Optimization: path compression

* compress the path
* later search will only use one iteration
* recommended

```cpp
int find_pc_twopass(int i) {
  vector<int> path;

  while (i != uf[i]) {
    path.push_back(i);
    i = uf[i];
  }

  for (int p : path) {
    uf[p] = i;
  }

  return i;
}
```

* if we need one path, compress it to grandparent
* effectively halves the path

```cpp
int find_pc_onepass(int i) {
    while (i != uf[i]) {
      uf[i] = uf[uf[i]];
      i = uf[i];
    }
    return i;
}
```

Another optimization is union by size. It requires extra memory.

* remember the size of the tree
* avoid deep trees
* not recommended

```cpp
vector<int> size(N, 1);
void union_size(int i, int j) {
  i = find(i)
  j = find(j);
  if (i==j) return;
  if (size[i] < size[j]) {
    uf[i] = uf[j];
    size[j] += size[i];
  } else {
    uf[j] = uf[i];
    size[i] += size[j];
  }
}
```

## Spanning Tree

### Kruskal's

Add edges from known ones with minimal weight until connected.

Use Union-Find to test connectivity.

```cpp
sort(edges.begin(), edges.end());
for(auto e:edges) {
  auto s = e->s, t = e->t;
  if(!connected(s,t)) union(s,t);
}
```

### Prim's

First choose a random node

Use a priority queue to find the next edge that adds a new node

*untested* example implementation below:

```cpp
int n_nodes = graph.n_nodes(); // total number of nodes

x->done = 1; n_nodes -= 1;

for (auto ne : x->edges) {
  pq.push(make_pair(-ne->dist, ne->node));
}

while (n_nodes && !pq.empty()) {
  auto t = pq.top(); pq.pop();
  Node* n = t.second;
  if (!n->done) {
    n->done = 1; n_nodes -= 1;
    for (auto ne : n->edges) {
      if (ne->node->done) continue;
      pq.push(make_pair(-ne->dist, ne->node));
    }
  }
}
```

Ideally we should update the priority somehow, i.e. no duplicated edges in queue.

## Topological Sort

Require no cycles exist.

Define three states for the searching:

* not discovered
* processing
* processed

Run DFS, add to ans when a node is processed.

```cpp
vector<bool> visited(N, false);
vector<int> order;
void t_sort(int u) {
  if (visited[u]) { return; }

  visited[u] = true;

  // adj is 2D adjacent matrix
  for (int i = 0; i < adj[u].size(); ++i) {
    t_sort(adj[u][i]);
  }

  order.push_back(u);
}

for (int u = 0; u < n; u++) {
  t_sort(u);
}

// The "order" vector's order is "reversed" topological sort, reverse it back
reverse(order.begin(), order.end());
```

Another way is by using decreasing post number of DFS.

* a post number is a counter incremented when the code finishes visiting a vertex
  * when all its children are visited
* the code above is effectively DFS (by using the recursion stack)
  * and reverse the result gets the decreasing post number

Another iterative way:

```cpp
// adjacent list
vector<vector<int>> aj(n, vector<int>());
// in-degrees
vector<int> dg(n, 0);
// build from list of edges
for(pair<int, int>& edge:edges) {
    aj[edge.first].push_back(edge.second);
    dg[edge.second] += 1;
}

queue<int> q;

// start from root nodes (in-degree == 0)
for(int i = 0; i < n; ++i) {
    if(!dg[i]) q.push(i);
}

int c;
vector<int> result;
while (q.size()) {
    c = q.front();
    q.pop();
    result.push_back(c);
    
    for(int e:aj[c]) {
        // finished visiting all parents, in-degree becomes 0
        if(!(--dg[e])) q.push(e);
    }
}
```

## Reference

* [Competitive programming books](https://cses.fi/book/index.html)
* [Graph - Unweighted Graphs](https://algo.is/aflv16/aflv_07_graphs_1.pdf)
* [DS](https://dsa.cs.tsinghua.edu.cn/~deng/ds/index.htm)
