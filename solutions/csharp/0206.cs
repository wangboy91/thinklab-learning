public class ListNode {
    public int val;
    public ListNode next;
    public ListNode(int val = 0, ListNode next = null) { this.val = val; this.next = next; }
}
public class Solution {
    public ListNode ReverseList(ListNode head) {
        ListNode previous = null, current = head;
        while (current != null) {
            ListNode nextSaved = current.next;
            current.next = previous;
            previous = current;
            current = nextSaved;
        }
        return previous;
    }
}
