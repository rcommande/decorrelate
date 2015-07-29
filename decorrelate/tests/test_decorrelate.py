import pytest


@pytest.fixture
def clean_registry():
    import decorrelate
    registry = decorrelate.get_registry()

    registry._registered = {}


def test_get_proxy(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def func():
        pass

    def callback():
        pass

    decorrelate.get_proxy(func, callback)

    assert len(registry) == 1


def test_get_proxy_with_category(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def func():
        pass

    def callback():
        pass

    decorrelate.get_proxy(func, callback, category='test_category')

    assert len(registry) == 1


def test_original(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def decorator(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        decorrelate.get_proxy(wrapped, callback)
        return wrapped

    @decorator
    def test_func():
        pass

    assert hasattr(test_func, 'wrapped') is False
    assert len(registry) == 1


def test_activates(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def decorator(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        return decorrelate.get_proxy(wrapped, callback)

    @decorator
    def test_func():
        pass

    assert hasattr(test_func, 'wrapped') is False
    assert len(registry) == 1

    decorrelate.activates()

    assert hasattr(test_func, 'wrapped')
    assert len(registry) == 0


def test_activates_proxy_attributes(clean_registry):
    import decorrelate

    def decorator(wrapped):
        def callback(callable):
            callable.wrapped = True
            callable.__doc__ = 'A test function after wrapping'
            return callable
        return decorrelate.get_proxy(wrapped, callback)

    @decorator
    def test_func():
        """A test function"""
        pass

    assert test_func.__doc__ == 'A test function'
    assert isinstance(test_func, decorrelate.Proxy)
    assert test_func.__name__ == 'test_func'
    assert not repr(test_func).startswith('<decorrelate.Proxy object')

    decorrelate.activates()

    assert test_func.__doc__ == 'A test function after wrapping'
    assert isinstance(test_func, decorrelate.Proxy)
    assert test_func.__name__ == 'test_func'
    assert not repr(test_func).startswith('<decorrelate.Proxy object')


def test_activates_decorator_with_parameter(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def decorator(value, **kwargs):
        def wrapper(wrapped):
            def callback(callable):
                callable.wrapped = True
                callable.value = value
                for key, val in kwargs.items():
                    setattr(callable, key, val)
                return callable
            decorrelate.get_proxy(wrapped, callback)
            return wrapped
        return wrapper

    @decorator('My value', one=1, two=2, three=3)
    def test_func():
        pass

    assert hasattr(test_func, 'wrapped') is False
    assert hasattr(test_func, 'value') is False
    assert hasattr(test_func, 'one') is False
    assert hasattr(test_func, 'two') is False
    assert hasattr(test_func, 'three') is False
    assert len(registry) == 1

    decorrelate.activates()

    assert hasattr(test_func, 'wrapped')
    assert hasattr(test_func, 'value')
    assert test_func.value == 'My value'
    assert hasattr(test_func, 'one')
    assert test_func.one == 1
    assert hasattr(test_func, 'two')
    assert test_func.two == 2
    assert hasattr(test_func, 'three')
    assert test_func.three == 3
    assert len(registry) == 0


def test_activates_with_category(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def decorator(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        decorrelate.get_proxy(wrapped, callback, category='a category')
        return wrapped

    def decorator2(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        decorrelate.get_proxy(wrapped, callback)
        return wrapped

    @decorator
    def test_func():
        pass

    @decorator2
    def test_func2():
        pass

    assert hasattr(test_func, 'wrapped') is False
    assert len(registry) == 2

    decorrelate.activates(category='a category')

    assert hasattr(test_func, 'wrapped')
    assert len(registry) == 1
    assert len(registry._registered['default']) == 1
    assert len(registry._registered['a category']) == 0


def test_activates_with_same_category(clean_registry):
    import decorrelate
    registry = decorrelate.get_registry()

    def decorator(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        decorrelate.get_proxy(wrapped, callback, category='a category')
        return wrapped

    def decorator2(wrapped):
        def callback(callable):
            callable.wrapped = True
            return callable
        decorrelate.get_proxy(wrapped, callback, category='a category')
        return wrapped

    @decorator
    def test_func():
        pass

    @decorator2
    def test_func2():
        pass

    assert hasattr(test_func, 'wrapped') is False
    assert len(registry) == 2

    decorrelate.activates(category='a category')

    assert hasattr(test_func, 'wrapped')
    assert len(registry) == 0
    assert len(registry._registered['a category']) == 0


def test_singleton(clean_registry):
    import decorrelate

    assert decorrelate.get_registry() == decorrelate.get_registry()
    assert id(decorrelate.get_registry()) == id(decorrelate.get_registry())
