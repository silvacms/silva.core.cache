# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import beaker.cache
import beaker.container
from beaker.cache import CacheManager as BCM
from beaker.exceptions import BeakerException

from five import grok
from App.config import getConfiguration
from silva.core.cache.interfaces import ICacheManager


logger = logging.getLogger('silva.core.cache')


def reset_beaker_caches():
    beaker.cache.cache_regions.clear()
    beaker.cache.cache_managers.clear()
    beaker.container.MemoryNamespaceManager.namespaces.clear()


try:
    from infrae.testing import testCleanUp
except ImportError:
    pass
else:
    testCleanUp.add(reset_beaker_caches)


class CacheManager(grok.GlobalUtility):
    """ a cache manager that wraps beaker
    """
    grok.implements(ICacheManager)
    grok.provides(ICacheManager)

    default_region_options = {
        'lock_dir': '/tmp/beaker',
        'type': 'memorylru',
        'max_items': '1000',
    }

    def __init__(self):
        self._parse_config()
        self.bcm = BCM(**self._parse_config())
        self.regions = self.bcm.regions

    def get_cache_from_region(self, namespace, region):
        try:
            return self.bcm.get_cache_region(namespace, region)
        except BeakerException as e:
            logger.warn('no specific configuration for region %s'
                        ' using defaults (%s) : %s',
                        region, repr(self.default_region_options), e)
            self._create_region_from_default(region)
            return self.bcm.get_cache_region(namespace, region)

    def get_cache(self, namespace, **options):
        # Doesn't rely on region for configuration.
        return self.bcm.get_cache(namespace, **options)

    def _parse_config(self):
        zconf = getattr(getConfiguration(), 'product_config', {})
        cache_config = zconf.get('silva.core.cache', {})
        regions = {}
        for key, value in cache_config.iteritems():
            if '.' in key:
                try:
                    region, param = key.split('.', 1)
                except ValueError:
                    continue

                if region not in regions:
                    regions[region] = {}
                regions[region][param] = value

        if regions.has_key('default'):
            self.default_region_options = regions['default']
            del regions['default']

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
