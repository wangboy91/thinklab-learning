def is_palindrome(s: str) -> bool:
    def valid(c: str) -> bool:
        return ('a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9')
    left, right = 0, len(s) - 1
    while left < right:
        if not valid(s[left]):
            left += 1
            continue
        if not valid(s[right]):
            right -= 1
            continue
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
