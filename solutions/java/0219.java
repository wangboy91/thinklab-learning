import java.util.HashSet;
import java.util.Set;
class Solution {
    public boolean containsNearbyDuplicate(int[] nums, int k) {
        if (k <= 0) return false;
        Set<Integer> seen = new HashSet<>();
        for (int i = 0; i < nums.length; i++) {
            if (seen.contains(nums[i])) return true;
            seen.add(nums[i]);
            if (i >= k) seen.remove(nums[i - k]);
        }
        return false;
    }
}
