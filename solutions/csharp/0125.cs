public class Solution {
    private bool IsAscii(char c) => (c >= 'a' && c <= 'z') ||
        (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9');
    public bool IsPalindrome(string s) {
        int left = 0, right = s.Length - 1;
        while (left < right) {
            if (!IsAscii(s[left])) { left++; continue; }
            if (!IsAscii(s[right])) { right--; continue; }
            if (char.ToLowerInvariant(s[left]) != char.ToLowerInvariant(s[right]))
                return false;
            left++; right--;
        }
        return true;
    }
}
