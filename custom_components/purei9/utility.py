def first_or_default(collection, predicate, default = None):
    for item in collection:
        if predicate(item):
            return item

    return None
