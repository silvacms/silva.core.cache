try:
    import pylibmc as memcache
except ImportError:
    import memcache

try:
    import threading
except ImportError:
    import dummy_threading as threading

import sys
from collections import deque
import time as clock
from App.config import getConfiguration


class LRU(object):

    def __init__(self, size):
        self.lock = threading.Lock()
        self.data = {}
        self.usage = deque([], size)
        self.cursor = 0
        self.size = size

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
            self.usage.remove(key)
            self.usage.append(key)
        finally:
            self.lock.release()

    def _del(self):
        old = self.usage.popleft()
        del self.data[old]


_memcache_url = None
_tlocal = threading.local()
_cache = LRU(1000)
_lock = threading.Lock()

def _get_memcache_url():
    global _memcache_url
    if _memcache_url is not None:
        return _memcache_url
    zconf = getattr(getConfiguration(), 'product_config', {})
    cache_config = zconf.get('silva.core.cache', {})
    _memcache_url = cache_config.get('memcache', 'memory')
    return _memcache_url

def _get_memcache_client():
    global _tlocal, _cache, _lock
    client = getattr(_tlocal, '_memcache_client', None)
    if client is None:
        memcache_url = _get_memcache_url()
        if memcache_url == 'memory':
            return MemcacheFakeClient(_cache, _lock)
        else:
            addresses = memcache_url.split(";")

        client = _tlocal._memcache_client = memcache.Client(addresses)
    return client


class MemcacheFakeClient(object):
    """ Fake memcache client
    """

    def __init__(self, cache, lock):
        self._cache = cache
        self._mutex = lock

    def get(self, key):
        return self._unwrap(self._cache.get(key))

    def set(self, key, value, time=0):
        return self._cache.put(key, self._wrap(value, time=0))

    def add(self, key, value, time=0):
        self._mutex.acquire()
        try:
            if self.get(key) is None:
                self.set(key, value, time)
                return True
            return False
        finally:
            self._mutex.release()

    def incr(self, key, delta=1):
        self._mutex.acquire()
        try:
            wrapper = self._cache.get(key)
            if wrapper is None:
                return None
            value = self._unwrap(wrapper)
            wrapper['value'] = int(value) + delta
            self._cache.put(key, wrapper)
            return wrapper['value']
        finally:
            self._mutex.release()

    def decr(self, key, delta=1):
        self.incr(self, key, -delta)

    def get_multi(self, keys, key_prefix=''):
        result = {}
        for key in keys:
            value = self.get(key_prefix + key)
            if value is not None:
                result[key] = value
        return result

    def _wrap(self, value, time):
        if time > 0:
            return {'value': value, 'expire': clock.time() + time}
        return {'value': value}

    def _unwrap(self, value):
        if value is None:
            return None
        if value.has_key('expire'):
            if value['expire'] < clock.time():
                return None
        return value['value']


class Memcache(object):

    def __init__(self, name, client=None):
        self.name = name
        if client is not None:
            self._memcache = client
        else:
            self._memcache = _get_memcache_client()

    def _get_namespaced_key(self, key):
        return self.name + ':' + str(key)

    def add(self, key, value, time=0):
        key = self._get_namespaced_key(key)
        self._memcache.add(key, value, time)

    def get(self, key):
        key = self._get_namespaced_key(key)
        return self._memcache.get(key)

    def set(self, key, value, time=0):
        key = self._get_namespaced_key(key)
        return self._memcache.set(key, value, time)

    def incr(self, key, delta=1):
        key = self._get_namespaced_key(key)
        return self._memcache.incr(key, delta=delta)

    def get_multi(self, keys):
        return self._memcache.get_multi(keys, self.name + ":")


class MemcacheSlice(Memcache):
    _index_key = '__index__'

    def __init__(self, name, client=None):
        super(MemcacheSlice, self).__init__(name, client=client)

    def get_index(self):
        index = self._get_internal_index()
        if index is None:
            return -1
        return index - 1

    def __len__(self):
        return self.get_index() + 1

    def _get_internal_index(self):
        index = self.get(self._index_key)
        if index is None:
            return None
        return int(index)

    def increment_index(self):
        if self._get_internal_index() is None:
            self.add(self._index_key, 0)
        return self.incr(self._index_key)

    def push(self, data):
        index = self.increment_index()
        return self.set(str(index), data)

    def __getslice__(self, start, end):
        if end is None or end == sys.maxint:
            end = self._get_internal_index()
        if start is None:
            start = 0
        if start >= end:
            return []
        keys = [str(index) for index in range(start + 1, end + 1)]
        mapped = self.get_multi(keys)
        return [mapped[key] for key in sorted(mapped.keys())]


