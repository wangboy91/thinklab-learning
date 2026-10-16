class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}
class Solution {
    public ListNode reverseList(ListNode head) {
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
