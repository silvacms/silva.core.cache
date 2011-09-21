try:
    import threading
except ImportError:
    import dummy_threading as threading

from collections import deque



class LRU(object):

    def __init__(self, size):
        self.lock = threading.Lock()
        self.size = size
        self.empty()

    def empty(self):
        self.lock.acquire()
        try:
            self.data = {}
            self.usage = deque([], self.size)
            self.cursor = 0
        finally:
            self.lock.release()

    def get(self, key, default=None):
        try:
            value = self.data[key]
            self._use(key)
            return value
        except KeyError:
            return default

    def put(self, key, value):
        if key in self.data:
            self._use(key)
            self.data[key] = value
            return

        self.lock.acquire()
        try:
            if len(self.data) > self.size:
                self._del()
            self.data[key] = value
            self.usage.append(key)
        finally:
            self.lock.release()

    def _use(self, key):
        self.lock.acquire()
        try:
            try:
                self.usage.remove(key)
            except ValueError:
                pass
            self.usage.append(key)
        finally:
            self.lock.release()

    def _del(self):
        old = self.usage.popleft()
        del self.data[old]


