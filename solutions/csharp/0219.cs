using System.Collections.Generic;
public class Solution {
    public bool ContainsNearbyDuplicate(int[] nums, int k) {
        if (k <= 0) return false;
        var seen = new HashSet<int>();
        for (int i = 0; i < nums.Length; i++) {
            if (seen.Contains(nums[i])) return true;
            seen.Add(nums[i]);
            if (i >= k) seen.Remove(nums[i - k]);
        }
        return false;
    }
}
