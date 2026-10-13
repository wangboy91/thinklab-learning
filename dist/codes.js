window.CODES={
1:{
'C#':`using System;
using System.Collections.Generic;
public class Solution {
    public int[] TwoSum(int[] nums, int target) {
        var seen = new Dictionary<int, int>();
        for (int i = 0; i < nums.Length; i++) {
            int need = target - nums[i];
            if (seen.TryGetValue(need, out int j))
                return new[] { j, i };
            seen[nums[i]] = i;
        }
        return Array.Empty<int>();
    }
}`,
'Python':`def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], i]
        seen[value] = i
    return []`,
'Java':`import java.util.HashMap;
import java.util.Map;
class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int need = target - nums[i];
            if (seen.containsKey(need))
                return new int[]{seen.get(need), i};
            seen.put(nums[i], i);
        }
        return new int[0];
    }
}`,
'JavaScript（Node.js）':`function twoSum(nums, target) {
    const seen = new Map();
    for (let i = 0; i < nums.length; i++) {
        const need = target - nums[i];
        if (seen.has(need)) return [seen.get(need), i];
        seen.set(nums[i], i);
    }
    return [];
}`,
'TypeScript':`function twoSum(nums: number[], target: number): number[] {
    const seen = new Map<number, number>();
    for (let i = 0; i < nums.length; i++) {
        const need = target - nums[i];
        if (seen.has(need)) return [seen.get(need)!, i];
        seen.set(nums[i], i);
    }
    return [];
}`},
20:{
'C#':`using System.Collections.Generic;
public class Solution {
    public bool IsValid(string s) {
        var stack = new Stack<char>();
        var pairs = new Dictionary<char, char> {
            { ')', '(' }, { ']', '[' }, { '}', '{' }
        };
        foreach (char c in s) {
            if (pairs.ContainsKey(c)) {
                if (stack.Count == 0 || stack.Peek() != pairs[c])
                    return false;
                stack.Pop();
            } else stack.Push(c);
        }
        return stack.Count == 0;
    }
}`,
'Python':`def is_valid(s: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in pairs:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
        else:
            stack.append(char)
    return not stack`,
'Java':`import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
class Solution {
    public boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> pairs = Map.of(
            ')', '(', ']', '[', '}', '{');
        for (char c : s.toCharArray()) {
            if (pairs.containsKey(c)) {
                if (stack.isEmpty() || stack.peek() != pairs.get(c).charValue())
                    return false;
                stack.pop();
            } else stack.push(c);
        }
        return stack.isEmpty();
    }
}`,
'JavaScript（Node.js）':`function isValid(s) {
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
}`,
'TypeScript':`function isValid(s: string): boolean {
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
}`}};
