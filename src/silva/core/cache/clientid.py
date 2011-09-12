# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

import random
import sys
import time
from sha import sha as sha1

from five import grok

from silva.core.views.interfaces import IVirtualSite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.session.interfaces import IClientId
from zope.datetime import rfc1123_date


COOKIE_ID = 'silva_session'


class ClientId(grok.Adapter):
    grok.context(IBrowserRequest)
    grok.provides(IClientId)

    def create_id(self):
        return sha1(str(random.randrange(sys.maxint))).hexdigest()

    def expire(self):
        return rfc1123_date(time.time() + 12 * 3600)

    def path(self):
        return IVirtualSite(self.context).get_root().absolute_url_path()

    def __str__(self):
        if COOKIE_ID in self.context.cookies:
            return self.context.cookies[COOKIE_ID]
        session_id = self.create_id()
        self.context.response.setCookie(
            COOKIE_ID, session_id, path=self.path(), expires=self.expire())
        # We set the value in cookies as well in case we are reask to
        # provide an ID during this same request lifetime.
        self.context.cookies[COOKIE_ID] = session_id
        return session_id

