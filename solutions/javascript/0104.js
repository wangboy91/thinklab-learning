class TreeNode {
    constructor(val = 0, left = null, right = null) {
        this.val = val; this.left = left; this.right = right;
    }
}
function maxDepth(root) {
    if (root === null) return 0;
    const queue = [root];
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
