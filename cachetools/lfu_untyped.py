"""

Implementation Details
----------------------

Currently, LFUCache uses collections.Counter to keep track of which keys are
most frequently used, and uses Counter.most_common(1) to select the key to
evict when the cache is full.

This approach is fast and works fine until the cache becomes full and items
start to need to be discarded frequently
"""

import heapq

from .cache import Cache


class UntypedLFUCache(Cache):
    """Optimized LFU cache implementation when typed keys are not needed."""

    def __init__(self, maxsize, getsizeof=None):
        super().__init__(maxsize, getsizeof)
        self.__heap = []  # List[Tuple[List[int], Hashable]]
        self.__refcounts = {}  # Dict[Hashable, List[int]]

    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        value = cache_getitem(self, key)

        # Edge case: if in a subclass __missing__ is defined to insert a key,
        # *but* the key doesn't get inserted because it doesn't fit in the
        # cache, it won't have gone through __setitem__ and thus doesn't exist
        # in __refcounts. Because of this, we need this `if` guard here.
        if key in self.__refcounts:
            self.__refcounts[key][0] += 1
            heapq.heapify(self.__heap)
        return value

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        cache_setitem(self, key, value)
        if key in self.__refcounts:
            # Key already exists, so we need to re-sort the heap after adding 1
            # to the reference count.
            self.__refcounts[key][0] += 1
            heapq.heapify(self.__heap)
        else:
            # Key doesn't exist, so we can push this straight onto the heap.
            refcount_list = self.__refcounts.setdefault(key, [0])
            heapq.heappush(self.__heap, (refcount_list, key))

    def __delitem__(self, key, cache_delitem=Cache.__delitem__):
        """Delete a specific entry from the cache, ignoring LFU rules.

        This is an expensive operation and should be avoided. If you don't
        absolutely need to delete a specific key from the cache, consider using
        popitem() instead.
        """
        cache_delitem(self, key)

        # We gotta do a linear search for the key inside the heap.
        for i, (_refcount, current_key) in enumerate(self.__heap):
            if current_key == key:
                # Need to break out of the loop before deleting the heap entry.
                # We can't modify the object we're iterating over while the
                # iterator is still active.
                break
        else:  # pragma: nocover
            # This should never happen -- we know the key is in the heap.
            raise RuntimeError(
                'Found key in the cache but not in the controlling heap. This'
                ' is likely a bug in the cache implementation.'
            )

        del self.__heap[i]
        del self.__refcounts[key]
        heapq.heapify(self.__heap)

    def popitem(self):
        """Remove and return the `(key, value)` pair least frequently used."""
        if not self.__heap:
            # `from None` necessary to suppress exception context as in <3.7
            raise KeyError(self.__class__.__name__ + ' is empty') from None

        _refcount, key = heapq.heappop(self.__heap)
        value = super().__getitem__(key)

        super().__delitem__(key)
        del self.__refcounts[key]
        return key, value
