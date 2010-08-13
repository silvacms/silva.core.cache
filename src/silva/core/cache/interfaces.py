from zope.interface import Interface


class ICacheStore(Interface):
    """ A cache object to store and retrieve from
    """

    def put(key, value, **options):
        """ put item in the cache """

    def get(key, **options):
        """ get item from the cache """

    def has_key(key):
        """ key present in cache """

    def remove(key):
        """ remove from cache """

    def clear():
        """ the whole cached (namespace) """


class ICacheManager(Interface):
    """ An utility from which to get cache objects
    """

    def get_cache(namespace, region):
        """ return a ICacheStore for the region
        """
