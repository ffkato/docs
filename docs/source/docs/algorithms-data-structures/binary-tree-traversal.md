# Binary Tree Traversal

A binary tree: degrees of all nodes are $<=2$.

Say the leaf nodes have 2 null children, then each non-null node has one left and one right child (that can be null).

## Traversals

X: current node

| Traversal  | Order |
| ---------- | ----- |
| Pre-order  | X L R |
| In-order   | L X R |
| Post-order | L R X |

The recursive way is obvious but risks of using many stacks.

## Node

Define a node as:

```c++
struct Node {
  Node* lc;
  Node* rc;
  Node* parent; // some implementations do not have
};
```

## Successor

A successor is the next node to visit in the in-order traversal of current node.

Below is a function finding a successor. It requires a "parent" pointer.

```c++
Node* successorOf(Node* n){
  if(!n) return nullptr;
  if(n->rc) { // leftmost child of rc
    n = n->rc; while(n->lc) n = n->lc;
  } else { // parent of the ancestor that has n in its right sub tree
    while(n->parent && n->parent->rc && n->parent->rc==n) n = n->parent;
    n = n->parent;
  }
  return n;
}
```

## Pre-Order Traversal

Recursive:

```c++
template<typename F>
void preOrderTraverse(Node* x, F& visit) {
  if(!x) return;
  visit(x);
  preOrderTraverse(x->lc, visit);
  preOrderTraverse(x->rc, visit);
}
```

Easy to convert since it looks like two tail recursions.

Iterative way using the "left branch first" strategy:

```c++
template<typename F>
void preOrderTraverseIterative(Node* root, F& visit) {
  stack<Node*> st;
  if(root) st.push(root);
  while (!st.empty()) {
    auto *x = st.top();
    st.pop();
    while (x) {
      visit(x);
      if(x->rc) st.push(x->rc);
      x = x->lc;
    }
  }
}
```

Optimization: for a normal tree, the number of null nodes is much
smaller than the number of the other nodes; checking null each time
may be wasteful **in some cases**.

Remove null check (not always better):

```c++
template<typename F>
void preOrderTraverseIterative(Node* root, F& visit) {
  stack<Node*> st;
  st.push(root);
  while (!st.empty()) {
    auto *x = st.top();
    st.pop();
    while (x) {
      visit(x);
      st.push(x->rc);
      x = x->lc;
    }
  }
}
```

## In-Order Traversal

Recursive:

```c++
template<typename F>
void inOrderTraverse(Node* x, F& visit) {
  if(!x) return;
  inOrderTraverse(x->lc, visit);
  visit(x);
  inOrderTraverse(x->rc, visit);
}
```

Traversal for right subtree is tail recursive but the one for left is not.

We can apply the similar strategy:

```c++
template<typename F>
void inOrderTraverseIterative(Node* x, F& visit) {
  stack<Node*> st;
  while(x || !st.empty()) {
    if (x) {
      st.push(x);
      x = x->lc;
    } else { // x is null and stack is non-empty
      x = st.top();
      st.pop();
      visit(x);
      x = x->rc;
    }
  }
}
```

Another way using successor function above:

```c++
template<typename F>
void inOrderTraverseIterative(Node* x, F& visit) {
  while(1) {
    if(x->lc) {
      x=x->lc;
    } else {
      visit(x);
      while(!x->rc) {
        if(!(x = successorOf(x))) return;
        visit(x);
      }
      x=x->rc;
    }
  }
}
```

## Post-Order Traversal

Recursive:

```c++
template<typename F>
void postOrderTraverse(Node* x, F& visit) {
  if(!x) return;
  postOrderTraverse(x->lc, visit);
  postOrderTraverse(x->rc, visit);
  visit(x);
}
```

Hard to convert directly since both are not tail recursions.

One iterative way using the "furthest reachable left leaf" strategy:

```c++
template<typename F>
void postOrderTraverseIterative(Node* x, F& visit) {
  stack<Node*> st;
  if(x) st.push(x);
  while(!st.empty()) {
    if(x->parent != st.top()) {
      while(auto y = st.top()) {
        if(y->lc) {
          if(y->rc) st.push(y->rc);
          st.push(y->lc);
        } else {
          st.push(y->rc);
        }
      }
      st.pop();
    }
    x = st.top();
    st.pop();
    visit(x);
  }
}
```

## Read More

[Post order traversal of binary tree without recursion - Stack Overflow](https://stackoverflow.com/questions/1294701/post-order-traversal-of-binary-tree-without-recursion)
