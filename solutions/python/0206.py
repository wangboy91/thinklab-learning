class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode | None) -> ListNode | None:
    previous, current = None, head
    while current is not None:
        next_saved = current.next
        current.next = previous
        previous = current
        current = next_saved
    return previous
