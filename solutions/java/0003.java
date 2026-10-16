import java.util.HashSet;
import java.util.Set;
class Solution {
    public int lengthOfLongestSubstring(String s) {
        Set<Character> seen = new HashSet<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            while (seen.contains(s.charAt(right))) {
                seen.remove(s.charAt(left)); left++;
            }
            seen.add(s.charAt(right));
            int length = right - left + 1;
            if (length > best) best = length;
        }
        return best;
    }
}
