class ListNode {
    constructor(val = 0, next = null) { this.val = val; this.next = next; }
}
function mergeTwoLists(a, b) {
    const dummy = new ListNode(); let tail = dummy;
    while (a !== null && b !== null) {
        if (a.val <= b.val) { tail.next = a; a = a.next; }
        else { tail.next = b; b = b.next; }
        tail = tail.next;
    }
    tail.next = a !== null ? a : b;
    return dummy.next;
}
