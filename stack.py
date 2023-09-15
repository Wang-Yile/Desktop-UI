class Stack():

    def __init__(self, default = None):

        self._sta = []
        self._default = default

    def __getitem__(self, index):

        return self._sta[index]
    
    def push(self, item):

        self._sta.append(item)
    
    def pop(self):

        if not self.empty():
            self._sta.pop()
    
    def top(self):

        if self.empty():
            return self._default
        return self._sta[-1]
    
    def size(self) -> int:

        return len(self._sta)
    
    def empty(self) -> bool:

        return True if len(self._sta) == 0 else False
