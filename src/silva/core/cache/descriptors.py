# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from persistent.interfaces import IPersistent
from silva.core.cache.interfaces import ICacheManager
from zope.component import getUtility
from beaker import util


def cached_method(namespace=None, region=None, key=None, **cache_options):
    def decorator(func):
        cache_ns = namespace
        if cache_ns is None:
            cache_ns = util.func_namespace(func)
        def cached_method(self, *args, **kwargs):
            utility = getUtility(ICacheManager)
            if region is not None:
                cache = utility.get_cache_from_region(cache_ns, region)
            else:
                cache = utility.get_cache(cache_ns, **cache_options)
            cache_key = None
            if key is not None:
                cache_key = key(self)
            if cache_key is None:
                cache_key = tuple()
                if IPersistent.providedBy(self):
                    cache_key = tuple(str(self._p_oid))
                cache_key += tuple(map(str, args))
                cache_key += tuple(map(lambda kwarg: "=".join(map(str, kwarg)),
                                       sorted(kwargs.items(),
                                              key=operator.itemgetter(0))))
                cache_key = " ".join(cache_key)
            def solves():
                return func(self, *args, **kwargs)
            return cache.get_value(cache_key, createfunc=solves)
        return cached_method
    return decorator


def cached_property(namespace=None, region=None, **cache_options):
    def decorator(func):
        cache_ns = namespace
        if cache_ns is None:
            cache_ns = util.func_namespace(func)
        def cached_property(self):
            utility = getUtility(ICacheManager)
            if region is not None:
                cache = utility.get_cache_from_region(cache_ns, region)
            else:
                cache = utility.get_cache(cache_ns, **cache_options)
            cache_key = 'property'
            if IPersistent.providedBy(self):
                cache_key = str(self._p_oid)
            def solves():
                return func(self)
            return cache.get_value(cache_key, createfunc=solves)
        return property(cached_property)
    return decorator
