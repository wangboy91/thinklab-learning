function lengthOfLongestSubstring(s: string): number {
    const seen = new Set<string>();
    let left = 0, best = 0;
    for (let right = 0; right < s.length; right++) {
        while (seen.has(s[right])) { seen.delete(s[left]); left++; }
        seen.add(s[right]);
        const length = right - left + 1;
        if (length > best) best = length;
    }
    return best;
}
