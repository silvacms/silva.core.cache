# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from infrae.testing import ZCMLLayer
from silva.core.cache.beakercache import reset_beaker_caches
import silva.core.cache

class CacheLayer(ZCMLLayer):

    def testTearDown(self):
        # reset beaker caches.
        reset_beaker_caches()


FunctionalLayer = CacheLayer(silva.core.cache, zcml_file='configure.zcml')
