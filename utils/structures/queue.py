from collections import deque
class Queue:
    def __init__(self):
        """Initializes an empty queue using deque."""
        self.items = deque()

    def enqueue(self, item):
        """Adds an element to the end of the queue — O(1)."""
        self.items.append(item)
    def dequeue(self):
        """Removes and returns the first element — O(1)."""
        if self.is_empty():
            return None
        return self.items.popleft()

    def front(self):
        """Returns the first element without removing it."""
        if self.is_empty():
            return None
        return self.items[0]

    def rear(self):
        """Returns the last element without removing it."""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        """Checks whether the queue is empty."""
        return len(self.items) == 0