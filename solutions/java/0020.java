import java.util.ArrayDeque;
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
}
