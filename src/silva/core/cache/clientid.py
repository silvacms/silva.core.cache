# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.session.interfaces import IClientId


class ClientId(grok.Adapter):
    grok.context(IBrowserRequest)
    grok.provides(IClientId)

    def __str__(self):
        return str(self.context.SESSION.id)
