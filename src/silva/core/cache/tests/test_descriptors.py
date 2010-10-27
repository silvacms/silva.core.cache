# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import beaker.cache

from zope.component import queryUtility

from silva.core.cache.interfaces import ICacheManager, _verify_key
from silva.core.cache.descriptors import cached_method, cached_property
from silva.core.cache.testing import FunctionalLayer


class TestContent(object):

    def __init__(self):
        self.value = 0

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


class DescriptorTestCase(unittest.TestCase):
    layer = FunctionalLayer

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
