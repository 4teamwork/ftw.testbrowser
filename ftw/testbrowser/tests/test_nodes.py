from ftw.testbrowser import browsing
from ftw.testbrowser.nodes import LinkNode
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
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
    def test_browser_root_is_wrapped(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(NodeWrapper, type(browser.root))

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

    @browsing
    def test_find_link_on_node(self, browser):
        browser.open(view='test-elements')
        body = browser.css('body').first
        link = body.find('A link with sub elements')
        self.assertEquals('link/target', link.attrib['href'])

    @browsing
    def test_find_textfield_on_node_by_label(self, browser):
        browser.visit(view='test-elements')
        body = browser.css('body').first
        self.assertEquals('field value', body.find('A textfield').value)

    @browsing
    def test_find_on_node_is_wrapped(self, browser):
        browser.open(view='test-elements')
        body = browser.css('body').first
        self.assertEquals(LinkNode, type(body.find('A link')))

    @browsing
    def test_element_is_within_other_element(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Foo')
        container = browser.css('.foo').first
        self.assertTrue(link.within(container))

    @browsing
    def test_element_is_not_within_other_element(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Baz')
        container = browser.css('.foo').first
        self.assertFalse(link.within(container))

    @browsing
    def test_element_contains_other_element(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Foo')
        container = browser.css('.foo').first
        self.assertTrue(container.contains(link))

    @browsing
    def test_element_does_not_contain_other_element(self, browser):
        browser.open(view='test-structure')
        link = browser.find('Link in Baz')
        container = browser.css('.foo').first
        self.assertFalse(container.contains(link))



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
