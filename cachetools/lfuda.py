import collections
import itertools

from .cache import Cache


class LFUDACache(Cache):
    """Least Frequently Used with Dynamic Aging (LFUDA) cache implementation.

    This implements a variant called LFU with Dynamic Aging (LFUDA) that uses
    dynamic aging to accommodate shifts in the set of popular objects. It adds
    a cache age factor to the reference count when a new object is added to the
    cache or when an existing object is re-referenced.

    Why? Suppose an object was frequently accessed in the past but has become
    unpopular. It will remain in the cache for a long time, preventing newly or
    less popular objects from replacing it. By keeping track of when an item
    was last accessed, we can evict items that were popular a long time ago but
    haven't been accessed recently.
    """

    def __init__(self, maxsize, getsizeof=None):
        super().__init__(maxsize, getsizeof)
        self.__counter = collections.Counter()
        self.__age_factor = 0

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.__counter[key] -= self.__age_factor
        self.__age_factor += 1
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__counter[key] -= self.__age_factor
        self.__age_factor += 1

    def __delitem__(self, key):
        super().__delitem__(key)
        self.__age_factor = self.__counter.pop(key)

    def popitem(self):
        """Remove and return the `(key, value)` pair least frequently used."""
        if not self.__counter:
            raise KeyError(self.__class__.__name__ + ' is empty') from None

        value = super().__getitem__(key)
        self.__delitem__(key)
        return key, value
