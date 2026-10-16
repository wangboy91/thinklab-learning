function isValid(s) {
    const stack = [];
    const pairs = { ')': '(', ']': '[', '}': '{' };
    for (const c of s) {
        if (Object.hasOwn(pairs, c)) {
            if (!stack.length || stack[stack.length - 1] !== pairs[c])
                return false;
            stack.pop();
        } else stack.push(c);
    }
    return stack.length === 0;
}
