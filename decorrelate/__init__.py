import functools


class Registry(object):
    _registered = None

    def __init__(self):
        self._registered = {}

    def __len__(self):
        return len(list(self.__iter__()))

    def __iter__(self):
        return (value for categ in self._registered.values() for value in categ)


class Proxy(object):
    """Represents a callable proxy.
    Replaces the original callable and redirects to this callable or to the wrapped (decorated) callable if the proxy
     is activated or not"""
    _callable = None
    _callback = None

    def __init__(self, callable, callback):
        self._callable = callable
        self._callback = callback

    def __call__(self, *args, **kwargs):
        return self._callable(*args, **kwargs)

    @property
    def __dict__(self):
        result = dict(self._callable.__dict__)
        result.update({'_callable': self._callable, '_callback': self._callback})
        return result

    def __getattr__(self, attribute):
        return getattr(self._callable, attribute)

    def __repr__(self):
        return repr(self._callable)


def singleton():
    """Get a function who returns the unique instance of the registry"""
    registry = Registry()

    def return_the_registry():
        return registry

    return return_the_registry


get_registry = singleton()


def get_proxy(func, callback, category='default'):
    registry = get_registry()
    proxy = Proxy(func, callback)
    proxy = functools.wraps(func)(proxy)
    if category not in registry._registered:
        registry._registered[category] = []
    registry._registered[category].append(proxy)
    return proxy


def activates(category=None):
    registry = get_registry()
    proxys = (proxy
              for key, values in registry._registered.items()
              for proxy in values
              if category is None or category == key)
    for proxy in proxys:
        proxy._callable = proxy._callback(proxy._callable)
        proxy = functools.wraps(proxy._callable)(proxy)
        if category is None:
            registry._registered = {}
        else:
            registry._registered[category] = ()
