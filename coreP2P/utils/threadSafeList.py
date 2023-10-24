import trio
class ThreadSafeList:
    def __init__(self):
        self._list = []
        self._lock = trio.Lock()

    async def append(self, item):
        async with self._lock:
            self._list.append(item)

    async def remove(self, item):
        async with self._lock:
            self._list.remove(item)

    async def get_item(self, index):
        async with self._lock:
            return self._list[index]
    
    async def set_item(self, index, value):
        async with self._lock:
            self._list[index] = value

    async def length(self):
        async with self._lock:
            return len(self._list)
        
    async def clear(self):
        async with self._lock:
            self._list.clear()
    
    async def remove_index(self, index):
        async with self._lock:
            del self._list[index]
    
    async def get_list(self):
        res = None
        async with self._lock:
            res = self._list
        return res