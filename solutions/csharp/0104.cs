using System.Collections.Generic;
public class TreeNode {
    public int val;
    public TreeNode left, right;
    public TreeNode(int val = 0, TreeNode left = null, TreeNode right = null) {
        this.val = val; this.left = left; this.right = right;
    }
}
public class Solution {
    public int MaxDepth(TreeNode root) {
        if (root == null) return 0;
        var queue = new Queue<TreeNode>();
        queue.Enqueue(root);
        int depth = 0;
        while (queue.Count > 0) {
            int size = queue.Count;
            depth++;
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.Dequeue();
                if (node.left != null) queue.Enqueue(node.left);
                if (node.right != null) queue.Enqueue(node.right);
            }
        }
        return depth;
    }
}
