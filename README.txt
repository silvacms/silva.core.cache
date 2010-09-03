silva.core.cache
----------------

Cache support for silva.

Configuration sample (zope.conf) :

<product-config silva.core.cache>

    # default region
    default.lock_dir /tmp/memcache
    default.type ext:memcached
    default.url localhost:11211

    # shared region (must be a real shared cache when using zeo)
    shared.lock_dir /tmp/memcache
    shared.type ext:memcached
    shared.url someotherhost:11211

</product-config>
