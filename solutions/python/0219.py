def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
    if k <= 0:
        return False
    seen = set()
    for i in range(len(nums)):
        if nums[i] in seen:
            return True
        seen.add(nums[i])
        if i >= k:
            seen.remove(nums[i - k])
    return False
