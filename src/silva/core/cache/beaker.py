from five import grok
from beaker.cache import CacheManager as BCM
from beaker.cache import cache_regions
from beaker.util import parse_cache_config_options
from beaker.exceptions import BeakerException
from App.config import getConfiguration
from silva.core.cache.interfaces import ICacheManager


class CacheManager(grok.Utility):
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
        self.bcm = BCM(**parse_cache_config_options(self._get_beaker_config()))

    def get_cache(self, region):
        try:
            return BCM.get_cache_region()
        except BeakerException:
            self._create_region_from_default(region)
            return BCM.get_cache_region()

    def _parse_config(self):
        zconf = getattr(getConfiguration(), 'product_config', {})
        cache_config = zconf.get('silva.core.cache', {})
        self.regions = {}
        for key, value in cache_config:
            if '.' in key:
                region, param = key.split('.', 1)
                if region not in self.regions:
                    self.regions[region] = {}
                self.regions[region][param] = value
        if 'default' in self.regions:
            self.default_region_options = self.regions['default']
            del self.default_region_options['default']
        return self.regions

    def _get_beaker_config(self):
        regions = self.regions.keys()
        options = self.regions.copy()
        options['regions'] = ", ".join(regions)
        return options

    def _create_region_from_default(self, region):
        """ Create the region with default
        """
        options = self.default_region_options.copy()
        self.regions[region] = options
        cache_regions.update({region: options})
