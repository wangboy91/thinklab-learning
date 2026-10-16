class TreeNode {
    val: number;
    left: TreeNode | null;
    right: TreeNode | null;
    constructor(val = 0, left: TreeNode | null = null, right: TreeNode | null = null) {
        this.val = val; this.left = left; this.right = right;
    }
}
function maxDepth(root: TreeNode | null): number {
    if (root === null) return 0;
    const queue: TreeNode[] = [root];
    let head = 0, depth = 0;
    while (head < queue.length) {
        const levelEnd = queue.length;
        depth++;
        while (head < levelEnd) {
            const node = queue[head++];
            if (node.left !== null) queue.push(node.left);
            if (node.right !== null) queue.push(node.right);
        }
    }
    return depth;
}
