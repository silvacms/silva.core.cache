from zope.interface import Interface


class ICacheStore(Interface):
    """ A cache object to store and retrieve from
    """

    def put(key, value, **options):
        """ put item in the cache """

    def get(key, value, **options):
        """ get item from the cache """


class ICacheManager(Interface):
    """ An utility from which to get cache objects
    """

    def get_cache(namespace, region):
        """ return a ICacheStore for the region
        """
