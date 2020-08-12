from cachetools import LFUDACache

from . import test_lfu


class LFUDACacheTest(test_lfu.LFUCacheTest):

    Cache = LFUDACache
