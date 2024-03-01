"""General utility functions"""
def first_or_default(collection, predicate, default = None):
    """Find the first item in a collection, or return default"""
    for item in collection:
        if predicate(item):
            return item

    return default

def array_join(array, separator = ", "):
    """Join an array of strings with a separator"""
    return separator.join(
        filter(
            lambda x: len(x) > 0,
            [str(item) for item in array if item is not None]
        )
    )
