function containsNearbyDuplicate(nums, k) {
    if (k <= 0) return false;
    const seen = new Set();
    for (let i = 0; i < nums.length; i++) {
        if (seen.has(nums[i])) return true;
        seen.add(nums[i]);
        if (i >= k) seen.delete(nums[i - k]);
    }
    return false;
}
