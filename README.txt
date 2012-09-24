================
silva.core.cache
================

Presentation
============

This package provide a pluggable cache support for Silva related
components, base on `Beaker <http://beaker.groovie.org/index.html>`_.
By default content will be cached in memory, but you can use a different
storage like files, memcache or an SQL database to store cached content.

For a single instance installation we recommand to use memory as
storage. For a ZEO / multi Zope instance installation we recommand to
use memcache as storage.

To use memcache recommend to install `pylibmc`, this can be done via
buildout. Please refer to the installation documentation of Silva for
this.

After you can configure in your Zope configuration
(``zope.conf``) which storage to use for which regions::

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

API
===

Developers have different tools at their disposal, mainly:

``silva.core.cache.descriptors.cached_method``
   Decorator that can be used on a class method to cache its
   computation. It can take a ``region`` which specify which caching
   region to use, a ``key`` which is a callable, taking as parameter
   the class on which the method is called to compute a caching
   key. If ``region`` is not specified, all other parameters are Beaker
   options used to configured the cache manager used.

``silva.core.cache.descriptors.cached_property``
   Decorator that can be used on a class to create a read-only
   property where its computation is cached in Beaker. Except for
   ``key`` it takes the same parameters than ``cached_method``.

``silva.core.cache.store.Store``
   Giving a cache name, it give a dictionnary like access to this
   cache.

``silva.core.cache.store.SessionStore``
   Constructed out of a request, it is a dictionnary like access to a
   unique cache for this user session. The session is identified with
   the help of the adapter ``IClientId`` of ``zope.session``. An
   implementation of this adapter for Zope 2 is done in this package.

``silva.core.cache.interfaces.ICacheManager``
   A global utility provides this interface to give you access to all
   cache managers used by this extension.

``silva.core.cache.memcacheutils.MemcacheSlice``
   Store a list of items in memcache.


Code repository
===============

The code for this extension can be found in Mercurial at:
https://hg.infrae.com/silva.core.cache
