# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.cache.interfaces import ICacheManager, _verify_key
from zope.component import getUtility
from zope.session.interfaces import IClientId

DEFAULT_REGION = 'shared'


class Store(object):
    """Abstract access to the cache manager.
    """

    def __init__(self, namespace, region=DEFAULT_REGION):
        cache_manager = getUtility(ICacheManager)
        self.__backend = cache_manager.get_cache_from_region(namespace, region)
        # Local key cache
        self.__keys = {}

    def _real_key(self, key):
        real_key = self.__keys.get(key)
        if real_key is None:
            real_key = _verify_key(key)
            self.__keys[key] = real_key
        return real_key

    def get(self, key, default=None):
        try:
            return self.__backend.get(self._real_key(key))
        except KeyError:
            return default

    def set(self, key, value):
        return self.__backend.put(self._real_key(key), value)

    def __getitem__(self, key):
        return self.__backend.get(self._real_key(key))

    __setitem__ = set

    def __contains__(self, key):
        return self.__backend.has_key(self._real_key(key))

    def __delitem__(self, key):
        self.__backend.remove(self._real_key(key))


class SessionStore(Store):
    """Store data within only current client scope.
    """

    def __init__(self, request, region=DEFAULT_REGION):
        super(SessionStore, self).__init__(
            'session:' + str(IClientId(request)), region=region)
