public class Solution {
    public void MoveZeroes(int[] nums) {
        int write = 0;
        for (int read = 0; read < nums.Length; read++) {
            if (nums[read] != 0) {
                nums[write] = nums[read];
                write++;
            }
        }
        for (int i = write; i < nums.Length; i++) nums[i] = 0;
    }
}
