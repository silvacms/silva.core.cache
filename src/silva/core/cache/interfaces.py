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

    def get_cache_from_region(namespace, region):
        """Return a beaker cache for this namespace, configured from
        the given region if it didn't exists.
        """

    def get_cache(namespace, **options):
        """Return a beaker cache for this namespace, constructed with
        the given options if it didn't exists.
        """
