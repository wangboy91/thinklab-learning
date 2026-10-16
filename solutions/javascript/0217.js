function containsDuplicate(nums) {
    const seen = new Set();
    for (const value of nums) {
        if (seen.has(value)) return true;
        seen.add(value);
    }
    return false;
}
