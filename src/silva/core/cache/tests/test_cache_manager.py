# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

import beaker.cache
from zope.interface.verify import verifyObject
from zope.component import queryUtility

from silva.core.cache.interfaces import ICacheManager
from silva.core.cache.testing import FunctionalLayer


class CacheManagerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def tearDown(self):
        beaker.cache.cache_regions.clear()

    def test_interface(self):
        manager = queryUtility(ICacheManager)
        self.assertNotEqual(manager, None)
        self.assertTrue(verifyObject(ICacheManager, manager))

    def test_create_region(self):
        manager = queryUtility(ICacheManager)
        cache = manager.get_cache_from_region('nstest', 'unexistant-region')
        self.assertTrue(cache)
        self.assertTrue('unexistant-region' in beaker.cache.cache_regions)

    def test_get_cache(self):
        manager = queryUtility(ICacheManager)
        cache = manager.get_cache('nstest')
        self.assertTrue(cache)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTestCase))
    return suite
