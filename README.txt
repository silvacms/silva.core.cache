silva.core.cache
----------------

Cache support for silva.

To use memcache you will need to add python-memcached or
python-libmemcached (C) to your buildout.

Configuration sample (zope.conf) :

<product-config silva.core.cache>

    # default region
    default.lock_dir /tmp/memcache
    default.type ext:memcached
    default.url localhost:11211

    # shared region
    shared.lock_dir /tmp/memcache
    shared.type ext:memcached
    shared.url someotherhost:11211

</product-config>
