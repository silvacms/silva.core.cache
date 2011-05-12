# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import beaker.cache

from zope.component import queryUtility

from silva.core.cache.interfaces import ICacheManager, _verify_key
from silva.core.cache.descriptors import (cached_method, cached_property,
                                          DontCache)
from silva.core.cache.testing import FunctionalLayer

def dontcache_key(self, *args, **kwargs):
    #a contrived key generator which raises DontCache when otherval is 0
    if self.otherval == 0:
        raise DontCache
    else:
        return "otherval"

class TestContent(object):

    def __init__(self):
        self.value = 0
        self.otherval = 0

    @cached_method(type='memory')
    def add(self, number):
        self.value += number
        return self.value

    @cached_method(region='test_descriptors')
    def remove(self, number):
        self.value -= number
        return self.value

    @cached_property(type='memory')
    def next(self):
        return self.value + 1
    
    @cached_method(key=dontcache_key)
    def get_otherval(self):
        return self.otherval
    
    @cached_property(key=dontcache_key)
    def get_prop(self):
        return self.otherval


class DescriptorTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_dontcache_method(self):
        #test to ensure that key generators raising dontcache actually are not
        # cached
        manager = queryUtility(ICacheManager)
        content = TestContent()
        #this method will not be cached if otherval is 0
        self.assertEqual(content.otherval, content.get_otherval())
        content.otherval = 1
        self.assertEqual(content.otherval, content.get_otherval())
        #now the method is cached, so changing otherval should have no effect
        content.otherval = 2
        self.assertEqual(1, content.get_otherval())
        
    def test_dontcache_property(self):
        #test to ensure that key generators raising dontcache actually are not
        # cached
        manager = queryUtility(ICacheManager)
        content = TestContent()
        #this method will not be cached if otherval is 0
        self.assertEqual(content.otherval, content.get_prop)
        content.otherval = 1
        self.assertEqual(content.otherval, content.get_prop)
        #now the method is cached, so changing otherval should have no effect
        content.otherval = 2
        self.assertEqual(1, content.get_prop)

    def test_method_simple(self):
        manager = queryUtility(ICacheManager)
        content = TestContent()
        self.assertEqual(content.add(4), 4)
        # The method is now cached, so add is not called.
        self.assertEqual(content.add(4), 4)

        cache = manager.get_cache(
            'silva.core.cache.tests.test_descriptors.add')
        self.assertEqual(cache.get(_verify_key(('4',))), 4)
        self.assertRaises(KeyError, cache.get, _verify_key(('5',)))

        self.assertEqual(content.add(5), 9)
        # The method is now cached, so add is not called.
        self.assertEqual(content.add(5), 9)

        self.assertEqual(cache.get(_verify_key(('4',))), 4)
        self.assertEqual(cache.get(_verify_key(('5',))), 9)

    def test_method_region(self):
        manager = queryUtility(ICacheManager)
        content = TestContent()
        self.assertEqual(content.remove(4), -4)
        # The method is now cached, so add is not called.
        self.assertEqual(content.remove(4), -4)

        self.assertTrue('test_descriptors' in beaker.cache.cache_regions)
        cache = manager.get_cache_from_region(
            'silva.core.cache.tests.test_descriptors.remove',
            'test_descriptors')
        self.assertEqual(cache.get(_verify_key(('4',))), -4)
        self.assertRaises(KeyError, cache.get, _verify_key(('-5',)))

        self.assertEqual(content.remove(-5), 1)
        # The method is now cached, so add is not called.
        self.assertEqual(content.remove(-5), 1)

        self.assertEqual(cache.get(_verify_key(('4',))), -4)
        self.assertEqual(cache.get(_verify_key(('-5',))), 1)

    def test_property(self):
        manager = queryUtility(ICacheManager)
        content = TestContent()
        content.add(4)

        cache = manager.get_cache(
            'silva.core.cache.tests.test_descriptors.next')
        self.assertRaises(KeyError, cache.get, 'property')

        self.assertEqual(content.next, 5)
        # The method is now cached, so it is recomputed.
        self.assertEqual(content.next, 5)

        self.assertEqual(cache.get('property'), 5)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DescriptorTestCase))
    return suite
