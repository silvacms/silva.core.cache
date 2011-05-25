# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator
import base64
from types import UnicodeType

from persistent.interfaces import IPersistent
from silva.core.cache.interfaces import ICacheManager, _verify_key
from zope.component import getUtility
from beaker import util


class DontCache(Exception):
    """to be raised by key generators when they determine the value of
       a particular method or property invocation should NOT be cached.
    """


def concat_args(*args, **kwargs):
    """serialize the positional and keyword arguments passed to the 
       "method to be cached" into a tuple of strings.
    """
    def encode(arg):
        #treat unicode strings specially (to preserve the encoded bytestring)
        if isinstance(arg, UnicodeType):
            return arg.encode('utf-8')
        else:
            return str(arg)
        
    key = tuple(map(encode, args))
    key += tuple(map(
        lambda kwarg: "=".join(map(encode, kwarg)),
        sorted(kwargs.items(), key=operator.itemgetter(0))))
    return key


def standard_method_key(self, func, *args, **kwargs):
    """The standard key generation for methods of objects.  Keys generated
       using this function are composed of the following:
       1) If 'self' is IPersistent, adds self._p_oid (so instances are unique)
       2) Serializes *args and **kwargs into a 1-tuple
    """
    
    cache_key = tuple()
    if IPersistent.providedBy(self):
        #_p_oid needs to be base64 encoded, as not all chars in the string
        # are in ascii range <128, so joining the key string will fail
        oid = base64.standard_b64encode(self._p_oid)
        cache_key += tuple([oid])
    cache_key += concat_args(*args, **kwargs)
    return cache_key


def cached_method(namespace=None, region='shared', key=standard_method_key,
                  expire=None, **cache_options):
    """create (return) a decorator on a method.  The vars in the above
       call (cached_method) are available within the decorator (a closure)
    """
    
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
            try:
                #generate the cache key (maybe using the standard method, or a
                # custom key generator).  Pass in the called function, in case
                # the key generator wants to do any argument introspection
                # or whatever.  `func` DOES NOT need to be added to the key
                cache_key = key(self, func, *args, **kwargs)
            except DontCache:
                # if the key generator determines that the particular method
                # invocation should NOT be cached, just call the function
                return func(self, *args, **kwargs)
            def solves():
                return func(self, *args, **kwargs)
            return cache.get_value(_verify_key(cache_key), createfunc=solves,
                expiretime=expire)
        return cached_method
    return decorator


def property_key(self):
    """standard key generator for properties.  Either 'property', or
       the _p_oid of the persistent object
    """
    cache_key = 'property'
    if IPersistent.providedBy(self):
        cache_key = str(self._p_oid)
    return cache_key


def cached_property(namespace=None, region=None, key=property_key,
                    expire=None, **cache_options):
    """create (return) a decorator on a property (read-only).  The vars in the 
       above call (cached_method) are available within the decorator (a closure)
    """

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
            #if the key generator raises a DontCache exception, just return
            # the property
            try:
                cache_key = key(self)
            except DontCache:
                return func(self)
            def solves():
                return func(self)
            return cache.get_value(_verify_key(cache_key), createfunc=solves,
                expiretime=expire)
        return property(cached_property)
    return decorator
