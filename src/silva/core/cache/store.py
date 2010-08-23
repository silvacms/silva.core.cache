# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.cache.interfaces import ICacheManager
from silva.core.cache.clientid import ClientId
from zope.component import getUtility


class Store(object):
    """Abstract access to the cache manager.
    """

    def __init__(self, namespace, region='shared'):
        cache_manager = getUtility(ICacheManager)
        self.__backend = cache_manager.get_cache(namespace, region)

    def get(self, key, default=None):
        try:
            return self.__backend.get(key)
        except KeyError:
            return default

    def set(self, key, value):
        return self.__backend.put(key, value)

    def __getitem__(self, key):
        return self.__backend.get(key)

    __setitem__ = set

    def __contains__(self, key):
        return self.__backend.has_key(key)

    def __delitem__(self, key):
        self.__backend.remove(key)


class SessionStore(Store):
    """Store data within only current client scope.
    """

    def __init__(self, request):
        super(SessionStore, self).__init__(str(ClientId(request)))
