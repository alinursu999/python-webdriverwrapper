# -*- coding: utf-8 -*-

from functools import wraps
import urlparse

__all__ = ('GoToPage', 'ShouldBeOnPage')


class GoToPage(object):
    """Decorator object for test method."""
    def __init__(self, path=None, query=None, domain=None):
        self.url_kwds = {
            'domain': domain,
            'path': path,
            'query': query,
        }

    def __call__(self, func):
        self.func = func
        return self.create_wrapper()

    def create_wrapper(self):
        @wraps(self.func)
        def f(self_of_wrapped_method):
            _append_domain(self_of_wrapped_method.driver, self.url_kwds)
            go_to_page(self_of_wrapped_method.driver, **self.url_kwds)
            self.func(self_of_wrapped_method)
        return f


class ShouldBeOnPage(object):
    """Decorator object for test method.
    After test this decorator check if page has expected url.
    """
    def __init__(self, path=None, query=None, domain=None):
        self.url_kwds = {
            'domain': domain,
            'path': path,
            'query': query,
        }

    def __call__(self, func):
        self.func = func
        return self.create_wrapper()

    def create_wrapper(self):
        @wraps(self.func)
        def f(self_of_wrapped_method):
            self.func(self_of_wrapped_method)
            _append_domain(self_of_wrapped_method.driver, self.url_kwds)
            url = _make_url(**self.url_kwds)
            self_of_wrapped_method.assertEqual(
                url,
                self_of_wrapped_method.driver.current_url,
                msg='"%s" url excepted after test, but is "%s".' % (
                    url,
                    self_of_wrapped_method.driver.current_url,
                ),
            )
        return f


def go_to_page(driver, path=None, query=None, domain=None):
    # If in url is present netloc, in path is probably whole url.
    if urlparse.urlparse(path).netloc:
        url = path
    else:
        url = _make_url(path, query, domain)
    driver.get(url)


def _make_url(path=None, query=None, domain=None):
    url = 'http://' + domain
    if path:
        url += '/' + path
    if query:
        url += '?'
        if isinstance(query, dict):
            url += '&'.join('%s=%s' % (k, v) for k, v in query.iteritems())
        else:
            url += query
    return url


def _append_domain(driver, url_kwds):
    url_kwds['domain'] = _get_domain(driver, url_kwds['domain'])


def _get_domain(driver, domain):
    if not domain:
        url = driver.current_url
        domain = urlparse.urlparse(url).netloc
    return domain
