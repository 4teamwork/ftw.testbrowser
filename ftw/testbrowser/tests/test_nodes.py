from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.form import Form
from ftw.testbrowser.nodes import LinkNode
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.nodes import Nodes
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestNodesResultSet(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_text_content_for_many_elements(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(['First link', 'Second link', 'Third link'],
                          browser.css('#some-links a').text_content())

    @browsing
    def test_normalized_text(self, browser):
        browser.open(view='test-structure')
        nodes = browser.css('.foo > *')

        self.assertEquals(
            {'default': ['Bar in Foo', 'Link in Foo'],
             'non-recursive': ['Bar in Foo', 'Link in']},
            {'default': nodes.normalized_text(),
             'non-recursive': nodes.normalized_text(recursive=False)})

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
    def test_child_css_selection(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#nested').xpath('em'),
                          browser.css('#nested').css('>em'))
        self.assertEquals(browser.css('#nested').xpath('em'),
                          browser.css('#nested').css('nonexistent, >em'))

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

    @browsing
    def test_find_within_result_set(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.find('Link in Baz'),
            browser.css('#content div').find('Link in Baz').first)

    @browsing
    def test_first_is_first_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#content > div')[0],
                          browser.css('#content > div').first)

    @browsing
    def test_first_raises_NoElementFound_when_nothing_matches(self, browser):
        browser.open(view='test-structure')
        with self.assertRaises(NoElementFound):
            browser.css('.not-existing-class').first

    @browsing
    def test_first_or_none_is_first_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#content > div')[0],
                          browser.css('#content > div').first_or_none)

    @browsing
    def test_first_is_None_when_nothing_matches(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(None, browser.css('.not-existing-class').first_or_none)

    @browsing
    def test_string_representation(self, browser):
        browser.open(view='test-structure')
        node = browser.css('.foo .bar')
        self.assertEquals(
            '<Nodes: [<NodeWrapper:span, class="bar", text:"Bar in Foo">]>',
            str(node))

    @browsing
    def test_result_set_equal_when_containing_same_nodes(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#content div'),
                          browser.css('#content div'),
                          'Two result sets with the same nodes should be equal.')

    @browsing
    def test_result_set_not_equal_when_containing_different_nodes(self, browser):
        browser.open(view='test-structure')
        self.assertNotEquals(browser.css('#content div'),
                             browser.css('#content a'),
                             'Two result sets with different nodes should not be'
                             ' equal.')

    @browsing
    def test_merging_two_Nodes_returns_result_set_as_well(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(Nodes, type(browser.css('.foo') + browser.css('.bar')))
        self.assertEquals(browser.css('.foo, .bar'),
                          browser.css('.foo') + browser.css('.bar'))

    @browsing
    def test_merging_list_with_Nodes_returns_Nodes(self, browser):
        browser.open(view='test-structure')
        result = list(browser.css('.foo')) + browser.css('.bar')
        self.assertEquals(Nodes, type(result))
        self.assertEquals(browser.css('.foo, .bar'), result)

    @browsing
    def test_Nodes_type_is_kept_on_append(self, browser):
        browser.open(view='test-structure')
        result = browser.css('.foo')
        result.append(browser.css('.bar').first)
        self.assertEquals(
            Nodes, type(result),
            'Appending to a "Nodes" object should not change it\'s type.')

    @browsing
    def test_Nodes_type_is_kept_on_extend(self, browser):
        browser.open(view='test-structure')
        result = browser.css('.foo')
        result.extend(browser.css('.bar'))
        self.assertEquals(
            Nodes, type(result),
            'Extending a "Nodes" object should not change it\'s type.')

    @browsing
    def test_Nodes_type_is_kept_on_remove(self, browser):
        browser.open(view='test-structure')
        result = browser.css('.foo, .bar')
        result.remove(browser.css('.bar').first)
        self.assertEquals(
            Nodes, type(result),
            'Removing from a "Nodes" object should not change it\'s type.')

    @browsing
    def test_Nodes_type_is_kept_on_pop(self, browser):
        browser.open(view='test-structure')
        result = browser.css('.foo, .bar')
        result.pop()
        self.assertEquals(
            Nodes, type(result),
            'Popping from a "Nodes" object should not change it\'s type.')

    @browsing
    def test_Nodes_type_is_kept_on_reverse(self, browser):
        browser.open(view='test-structure')
        result = browser.css('.foo, .bar')
        result.reverse()
        self.assertEquals(
            Nodes, type(result),
            'Reversing a "Nodes" object should not change it\'s type.')


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
    def test_forms_are_wrapped_into_form_nodes(self, browser):
        browser.open(view='test-elements')
        form = browser.css('#content form').first
        self.assertEquals(Form, type(form))

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
    def test_child_xpath_selection(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.xpath('//*[@id="nested"]/em'),
                          browser.xpath('//*[@id="nested"]').first.xpath('em'))

    @browsing
    def test_css_on_node(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(2, len(browser.css('span.bar')),
                          'Expected to find two ".bar" elements on the page.')

        foo = browser.css('div.foo').first
        self.assertEquals(1, len(foo.css('span.bar')),
                          'Expected to find one ".bar" element in ".foo".')

    @browsing
    def test_child_css_selection(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(browser.css('#nested > em'),
                          browser.css('#nested').first.css('>em'))
        self.assertEquals(browser.css('#nested > em'),
                          browser.css('#nested').first.css('nonexistent, >em'))

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

    @browsing
    def test_parent_by_css_returns_first_match(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('#content').first,
            browser.css('.foo > .bar').first.parent('#content'))

    @browsing
    def test_parent_by_css_returns_None_when_no_match(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            None,
            browser.css('.foo > .bar').first.parent('form'))

    @browsing
    def test_parent_by_xpath_returns_first_match(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('#content').first,
            browser.css('.foo > .bar').first.parent(xpath='*[@id="content"]'))

    @browsing
    def test_parent_by_xpath_returns_None_when_no_match(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            None,
            browser.css('.foo > .bar').first.parent(xpath='form'))

    @browsing
    def test_returns_first_parent_when_no_argument_passed(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('div.foo').first,
            browser.css('.foo > .bar').first.parent())

    @browsing
    def test_parent_does_not_allow_multiple_argument(self, browser):
        browser.open(view='test-structure')
        with self.assertRaises(ValueError) as cm:
            browser.css('.foo > .bar').first.parent(css='div', xpath='div')
        self.assertEquals('parent() requires either "css" or "xpath" argument.',
                          str(cm.exception))

    @browsing
    def test_normalized_text(self, browser):
        browser.open(view='test-structure')
        link = browser.css('.foo a').first

        self.assertEquals(
            {'default': 'Link in Foo',
             'non-recursive': 'Link in'},
            {'default': link.normalized_text(),
             'non-recursive': link.normalized_text(recursive=False)})

    @browsing
    def test_normalized_text_replaces_non_breaking_spaces(self, browser):
        browser.open(view='test-structure')
        self.assertEquals('Non breaking spaces.',
                          browser.css('.non-breaking').first.normalized_text())

    @browsing
    def test_nonrecursive_normalized_text_when_node_has_no_content(self, browser):
        browser.open(view='test-structure')
        node = browser.css('.empty').first
        self.assertEquals(None, node.text,
                          'Expected node ".empty" to not have any text.')
        self.assertEquals('', node.normalized_text(recursive=False))

    @browsing
    def test_classes(self, browser):
        browser.open(view='test-structure')
        self.assertIn('userrole-anonymous', browser.css('body').first.classes)


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

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_clicking_links(self, browser):
        browser.open().find('Site Map').click()
        self.assertEquals('sitemap', plone.view())


class TestDefinitionListNode(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_keys_returns_dts(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('#definition-list-of-links dt'),
            browser.css('#definition-list-of-links').first.keys())

    @browsing
    def test_terms_is_dts_as_text(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            ['Mails', 'Search', 'Maps'],
            browser.css('#definition-list-of-links').first.terms)

    @browsing
    def test_values_returns_dds(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            browser.css('#definition-list-of-links dd'),
            browser.css('#definition-list-of-links').first.values())

    @browsing
    def test_definitions_is_dds_as_text(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            ['mail.google.com', 'google.com', 'maps.google.com'],
            browser.css('#definition-list-of-links').first.definitions)

    @browsing
    def test_items_returns_list_of_dt_to_dd_mapping(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(zip(browser.css('#definition-list-of-links dt'),
                              browser.css('#definition-list-of-links dd')),
                          browser.css('#definition-list-of-links').first.items())

    @browsing
    def test_items_text_returns_list_of_dt_to_dd_mapping_as_text(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            [('Mails', 'mail.google.com'),
             ('Search', 'google.com'),
             ('Maps', 'maps.google.com')],
            browser.css('#definition-list-of-links').first.items_text())

    @browsing
    def test_text_to_nodes_returns_dict_of_text_terms_to_node_defs(self, browser):
        browser.open(view='test-structure')
        self.assertEquals(
            dict(zip(['Mails', 'Search', 'Maps'],
                     browser.css('#definition-list-of-links > dd'))),
            browser.css('#definition-list-of-links').first.text_to_nodes())
