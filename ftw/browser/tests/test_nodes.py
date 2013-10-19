from ftw.browser import browsing
from ftw.browser.nodes import LinkNode
from ftw.browser.nodes import NodeWrapper
from ftw.browser.pages import plone
from ftw.browser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestNodes(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_css_returns_wrapped_nodes(self, browser):
        browser.open(view='test-structure')
        body = browser.css('body').first
        self.assertEquals(NodeWrapper, type(body))

    @browsing
    def test_xpath_returns_wrapped_nodes(self, browser):
        browser.open(view='test-structure')
        body = browser.xpath('//body').first
        self.assertEquals(NodeWrapper, type(body))

    @browsing
    def test_find_returns_wrapped_nodes(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Foo')
        self.assertEquals(LinkNode, type(link))

    @browsing
    def test_getparent_returns_wrapped_node(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Foo')
        parent = link.getparent()
        self.assertEquals(NodeWrapper, type(parent))

    @browsing
    def test_xpath_on_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(2, len(browser.xpath('//span[@class="bar"]')),
                          'Expected to find two ".bar" elements on the page.')

        foo = browser.css('div.foo').first
        self.assertEquals(1, len(foo.xpath('span[@class="bar"]')),
                          'Expected to find one ".bar" element in ".foo".')

    @browsing
    def test_css_on_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(2, len(browser.css('span.bar')),
                          'Expected to find two ".bar" elements on the page.')

        foo = browser.css('div.foo').first
        self.assertEquals(1, len(foo.css('span.bar')),
                          'Expected to find one ".bar" element in ".foo".')

    @browsing
    def test_body_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        body = browser.css('.foo').first.body
        self.assertEquals(NodeWrapper, type(body))

    @browsing
    def test_find_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        body = browser.css('body').first
        node = body.find('*')
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_findall_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        body = browser.css('body').first
        node = body.findall('*').first
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_find_class_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        body = browser.css('body').first
        node = body.find_class('foo').first
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iter_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = tuple(foo.iter())[0]
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iterancestors_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = tuple(foo.iterancestors())[0]
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iterchildren_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = tuple(foo.iterchildren())[0]
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iterdescendants_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = foo.iterdescendants().first
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iterfind_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = foo.iterfind('*').first
        self.assertEquals(NodeWrapper, type(node))

    @browsing
    def test_iterlinks_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node, _attr, _link, _pos = tuple(foo.iterlinks())[0]
        self.assertEquals(LinkNode, type(node))

    @browsing
    def test_itersiblings_on_node_is_wrapped(self, browser):
        browser.open(view='test-structure')
        foo = browser.css('.foo').first
        node = foo.itersiblings().first
        self.assertEquals(NodeWrapper, type(node))


class TestNodeComparison(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_comparing_two_elements_representing_the_same_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('.foo a').first,
                          browser.css('.foo a').first,
                          'Looking up two time the same elements should compare '
                          'to be similar.')

    @browsing
    def test_comparing_different_elements(self, browser):
        browser.open(view='test-structure')
        self.assertNotEquals(browser.css('.foo').first,
                             browser.css('.foo').first.getparent(),
                             'Different elements should be different.')


class TestLinkNode(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_clicking_links(self, browser):
        browser.open().find('Site Map').click()
        self.assertEquals('sitemap', plone.view())
