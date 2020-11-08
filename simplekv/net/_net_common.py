LAZY_PROPERTY_ATTR_PREFIX = "_lazy_"


def lazy_property(fn):
    """Decorator that makes a property lazy-evaluated.

    On first access, lazy properties are computed and saved
    as instance attribute with the name `'_lazy_' + method_name`
    Any subsequent property access then returns the cached value."""
    attr_name = LAZY_PROPERTY_ATTR_PREFIX + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazy_property
