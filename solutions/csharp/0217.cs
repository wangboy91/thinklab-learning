using System.Collections.Generic;
public class Solution {
    public bool ContainsDuplicate(int[] nums) {
        var seen = new HashSet<int>();
        foreach (int value in nums) {
            if (seen.Contains(value)) return true;
            seen.Add(value);
        }
        return false;
    }
}
