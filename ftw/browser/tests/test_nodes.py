from ftw.browser import browsing
from ftw.browser.nodes import LinkNode
from ftw.browser.nodes import NodeWrapper
from ftw.browser.pages import plone
from ftw.browser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from unittest2 import TestCase



class TestNodesResultSet(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_text_content_for_many_elements(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(['First link', 'Second link', 'Third link'],
                          browser.css('#some-links a').text_content())

    @browsing
    def test_xpath_within_multiple_elements(self, browser):
        browser.open(view='test-structure')
        list_items = browser.css('#list-of-links li')
        links = list_items.xpath('a')
        self.assertEquals(['Link of first item', 'Link of second item'],
                          links.text_content())

    @browsing
    def test_css_within_multiple_elements(self, browser):
        browser.open(view='test-structure')
        list_items = browser.css('#list-of-links li')
        links = list_items.css('a')
        self.assertEquals(['Link of first item', 'Link of second item'],
                          links.text_content())

    @browsing
    def test_getparents_of_multiple_elements(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#list-of-links li'),
                          browser.css('#list-of-links li a').getparents())

    @browsing
    def test_getparents_of_multiple_elements_is_uniquified(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('#list-of-links'),
            browser.css('#list-of-links li').getparents(),
            'Expected only one parent, since all items are in the same list.')



class TestNodeWrappers(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_string_representation(self, browser):
        browser.open(view='test-structure')
        node = browser.css('.foo .bar').first
        self.assertEquals('<NodeWrapper:span, class="bar", text:"Bar in Foo">',
                          str(node))

    @browsing
    def test_string_representation_without_text(self, browser):
        browser.open(view='test-structure')
        node = browser.css('.foo').first
        self.assertEquals('<NodeWrapper:div, class="foo">', str(node))

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
