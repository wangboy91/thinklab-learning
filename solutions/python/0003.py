def length_of_longest_substring(s: str) -> int:
    seen = set()
    left = best = 0
    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        length = right - left + 1
        if length > best:
            best = length
    return best
