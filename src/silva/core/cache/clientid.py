# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import random
import sys
import hashlib
import time

from five import grok

from silva.core.views.interfaces import IVirtualSite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest
from zope.session.interfaces import IClientId
from zope.datetime import rfc1123_date


COOKIE_ID = 'silva_session'


class ClientId(grok.Adapter):
    grok.context(IBrowserRequest)
    grok.provides(IClientId)

    def create_id(self):
        return hashlib.sha1(str(random.randrange(sys.maxint))).hexdigest()

    def expire(self):
        return rfc1123_date(time.time() + 12 * 3600)

    def path(self):
        return IVirtualSite(self.context).get_top_level_path()

    def __str__(self):
        if COOKIE_ID in self.context.cookies:
            return self.context.cookies[COOKIE_ID]
        session_id = self.create_id()
        self.context.response.setCookie(
            COOKIE_ID, session_id,
            path=self.path(),
            expires=self.expire(),
            http_only=True)
        # We set the value in cookies as well in case we are reask to
        # provide an ID during this same request lifetime.
        self.context.cookies[COOKIE_ID] = session_id
        return session_id


# XXX This should be registered only for testing via a ftesting.zcml
class TestClientId(grok.Adapter):
    grok.context(TestRequest)
    grok.provides(IClientId)

    def __str__(self):
        return 'client-id'
