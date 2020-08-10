from cachetools import UntypedLFUCache

from . import test_lfu


class UntypedLFUCacheTest(test_lfu.LFUCacheTest):

    Cache = UntypedLFUCache
