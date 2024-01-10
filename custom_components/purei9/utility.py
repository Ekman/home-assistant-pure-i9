def first_or_default(collection, predicate, default = None):
    """Find the first item in a collection, or return default"""
    for item in collection:
        if predicate(item):
            return item

    return None
