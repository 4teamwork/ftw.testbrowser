from ftw.browser.core import Browser

browser = Browser()


def browsing(func):
    def test_function(self, *args, **kwargs):
        with browser(self.layer['app']):
            args = list(args) + [browser]
            return func(self, *args, **kwargs)
    test_function.__name__ = func.__name__
    return test_function
