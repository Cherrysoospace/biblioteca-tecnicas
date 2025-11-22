class Stack:
    def __init__(self):
        """Initializes an empty stack."""
        self.items = []

    def push(self, item):
        """Adds an element to the top of the stack."""
        self.items.append(item)

    def pop(self):
        """Removes and returns the top element."""
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        """Returns the top element without removing it."""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        """Checks whether the stack is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Returns the number of elements."""
        return len(self.items)