from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def max_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    queue = deque([root])
    depth = 0
    while queue:
        size = len(queue)
        depth += 1
        for _ in range(size):
            node = queue.popleft()
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
    return depth
