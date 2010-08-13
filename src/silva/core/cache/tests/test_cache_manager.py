import unittest
from silva.core.cache.beaker import CacheManager
# from zope.interface.verify import VerifyObject
from Products.Silva.tests.layer import SilvaFunctionalLayer


class CacheManagerTest(unittest.TestCase):
    layer = SilvaFunctionalLayer

    def setUp(self):
        self.cm = CacheManager()

    def test_create_region(self):
        cache = self.cm.get_cache('unexistant')
        self.assertTrue(cache)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheManagerTest))
    return suite

