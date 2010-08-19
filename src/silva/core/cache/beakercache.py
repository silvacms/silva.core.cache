# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import beaker.cache
from beaker.cache import CacheManager as BCM
from beaker.exceptions import BeakerException

from five import grok
from App.config import getConfiguration
from silva.core.cache.interfaces import ICacheManager

logger = logging.getLogger('silva.core.cache')


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

    def get_cache(self, namespace, region):
        try:
            return self.bcm.get_cache_region(namespace, region)
        except BeakerException:
            logger.warn('no specific configuration for region %s'
                        ' using defaults : %s',
                        region, repr(self.default_region_options))
            self._create_region_from_default(region)
            return self.bcm.get_cache_region(namespace, region)

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
