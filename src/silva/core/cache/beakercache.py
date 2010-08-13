from five import grok
import beaker.cache
from zope.interface import alsoProvides
from beaker.cache import CacheManager as BCM
from beaker.exceptions import BeakerException
from App.config import getConfiguration
from silva.core.cache.interfaces import ICacheManager, ICacheStore


class CacheManager(object):
    """ a cache manager that wraps beaker
    """
    grok.implements(ICacheManager)

    default_region_options = {
        'lock_dir': '/tmp/beaker',
        'type': 'memorylru',
        'max_items': '1000',
    }

    def __init__(self):
        self._parse_config()
        self.bcm = BCM(**self._parse_config())
        self.regions = self.bcm.regions

    def get_cache(self, namespace, region):
        try:
            return self.bcm.get_cache_region(namespace, region)
        except BeakerException:
            self._create_region_from_default(region)
            cache = self.bcm.get_cache_region(namespace, region)
            alsoProvides(ICacheStore, cache)

    def _parse_config(self):
        zconf = getattr(getConfiguration(), 'product_config', {})
        cache_config = zconf.get('silva.core.cache', {})
        regions = {}
        for key, value in cache_config:
            if '.' in key:
                region, param = key.split('.', 1)
                if region not in regions:
                    regions[region] = {}
                regions[region][param] = value
        options = self.default_region_options.copy()
        options['cache_regions'] = regions
        return options

    def _create_region_from_default(self, region):
        """ Create the region with default
        """
        options = self.default_region_options.copy()
        self.regions[region] = options
        self.bcm.regions.update({region: options})
        beaker.cache.cache_regions.update({region: options})


grok.global_utility(CacheManager)
