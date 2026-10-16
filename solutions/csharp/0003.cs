using System.Collections.Generic;
public class Solution {
    public int LengthOfLongestSubstring(string s) {
        var seen = new HashSet<char>();
        int left = 0, best = 0;
        for (int right = 0; right < s.Length; right++) {
            while (seen.Contains(s[right])) {
                seen.Remove(s[left]); left++;
            }
            seen.Add(s[right]);
            int length = right - left + 1;
            if (length > best) best = length;
        }
        return best;
    }
}
