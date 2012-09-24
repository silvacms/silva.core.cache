# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
import unittest
import threading
from silva.core.cache.memcacheutils import LRU, MemcacheFakeClient, MemcacheSlice


class TestMemoryImplementation(unittest.TestCase):

    def setUp(self):
        self.cache = LRU(1000)
        self.mutex = threading.Lock()
        self.memslice = MemcacheSlice(
            'test', client=MemcacheFakeClient(self.cache, self.mutex))

    def test_empty(self):
        self.assertEquals(-1, self.memslice.get_index())
        self.assertEquals(0, len(self.memslice))
        self.assertEquals([], self.memslice[:])
        self.assertEquals([], self.memslice[0:1])

    def test_simple_add(self):
        self.memslice.push('first')
        self.assertEquals(0, self.memslice.get_index())
        self.assertEquals(['first'], self.memslice[:])
        self.assertEquals(['first'], self.memslice[0:1])
        self.assertEquals(['first'], self.memslice[:1])

    def test_multiple_add(self):
        self.memslice.push('first')
        self.memslice.push('second')
        self.memslice.push('third')
        self.assertEquals(2, self.memslice.get_index())
        self.assertEquals(3, len(self.memslice))
        self.assertEquals(['first', 'second', 'third'], self.memslice[:])
        self.assertEquals(['first', 'second', 'third'], self.memslice[0:3])
        self.assertEquals(['second', 'third'], self.memslice[1:])

    def test_threaded_add(self):
        for run in range(0, 10):
            value_count = 40
            thread_count = 5

            threads = []
            cache = LRU((value_count + 1) * thread_count)
            memslice = MemcacheSlice(
                'test', client=MemcacheFakeClient(cache, self.mutex))

            def async_add():
                for i in range(0, value_count):
                    memslice.push(i)

            for i in range(0, thread_count):
                th = threading.Thread(target=async_add)
                threads.append(th)

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            self.assertEquals(thread_count * value_count, len(memslice),
                "run %d : %d/%d" % (
                    run + 1, len(memslice), thread_count * value_count))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMemoryImplementation))
    return suite
