function isPalindrome(s: string): boolean {
    const valid = (c: string): boolean => /[A-Za-z0-9]/.test(c);
    let left = 0, right = s.length - 1;
    while (left < right) {
        if (!valid(s[left])) { left++; continue; }
        if (!valid(s[right])) { right--; continue; }
        if (s[left].toLowerCase() !== s[right].toLowerCase()) return false;
        left++; right--;
    }
    return true;
}
