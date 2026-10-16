class ListNode {
    constructor(val = 0, next = null) { this.val = val; this.next = next; }
}
function reverseList(head) {
    let previous = null, current = head;
    while (current !== null) {
        const nextSaved = current.next;
        current.next = previous;
        previous = current;
        current = nextSaved;
    }
    return previous;
}
