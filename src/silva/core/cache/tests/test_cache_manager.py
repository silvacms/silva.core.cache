import unittest
from silva.core.cache.beakercache import CacheManager
from silva.core.cache.interfaces import ICacheManager
from zope.interface.verify import verifyObject
from Products.Silva.tests.layer import SilvaFunctionalLayer


class CacheManagerTest(unittest.TestCase):
    layer = SilvaFunctionalLayer

    def setUp(self):
        self.cm = CacheManager()

    def tearDown(self):
        import beaker.cache
        beaker.cache.cache_regions.clear()

    def test_interface(self):
        self.assertTrue(verifyObject(ICacheManager, self.cm))

    def test_create_region(self):
        cache = self.cm.get_cache('nstest', 'unexistant-region')
        self.assertTrue(cache)
        from beaker.cache import cache_regions
        self.assertTrue('unexistant-region' in cache_regions)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

