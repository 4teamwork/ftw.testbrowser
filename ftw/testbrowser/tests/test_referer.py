from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testbrowser.tests.alldrivers import all_drivers
from unittest2 import TestCase


@all_drivers
class TestReferer(TestCase):

    @browsing
    def test_no_referer_on_first_visit(self, browser):
        browser.open(view='test-dump-request')
        self.assert_referer('')

    @browsing
    def test_referer_set_when_clicking_links(self, browser):
        browser.open(view='test-referer')
        browser.find('Dump request').click()
        self.assert_referer(self.referer_view_url())

    @browsing
    def test_referer_set_when_submitting_forms(self, browser):
        browser.open(view='test-referer')
        browser.css('form#dumper').first.submit()
        self.assert_referer(self.referer_view_url())

    @browsing
    def test_referer_not_set_when_visiting_new_page(self, browser):
        browser.open()
        browser.open(view='test-dump-request')
        self.assert_referer('')

    @browsing
    def test_referer_set_when_reloading_page(self, browser):
        browser.open(view='test-referer')
        browser.find('Dump request').click()
        browser.reload()
        self.assert_referer(self.referer_view_url())

    @browsing
    def test_relative_link(self, browser):
        browser.open(view='test-referer')
        browser.css('#relative-link').first.click()

    def referer_view_url(self):
        return '/'.join((self.layer['portal'].absolute_url(),
                         'test-referer'))

    def assert_referer(self, expected):
        self.assertEquals(expected,
                          browser.json['HEADERS'].get('REFERER', ''))
