class ListNode {
    val: number;
    next: ListNode | null;
    constructor(val = 0, next: ListNode | null = null) { this.val = val; this.next = next; }
}
function reverseList(head: ListNode | null): ListNode | null {
    let previous: ListNode | null = null, current = head;
    while (current !== null) {
        const nextSaved: ListNode | null = current.next;
        current.next = previous;
        previous = current;
        current = nextSaved;
    }
    return previous;
}
