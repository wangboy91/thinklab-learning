function isValid(s: string): boolean {
    const stack: string[] = [];
    const pairs: Record<string, string> = { ')': '(', ']': '[', '}': '{' };
    for (const c of s) {
        if (Object.hasOwn(pairs, c)) {
            if (!stack.length || stack[stack.length - 1] !== pairs[c])
                return false;
            stack.pop();
        } else stack.push(c);
    }
    return stack.length === 0;
}
