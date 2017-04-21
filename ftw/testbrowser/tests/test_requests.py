from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver
from ftw.testbrowser.tests.helpers import register_view
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from zope.publisher.browser import BrowserView


@all_drivers
class TestBrowserRequests(FunctionalTestCase):

    def setUp(self):
        super(TestBrowserRequests, self).setUp()
        self.grant('Manager')
        self.json_view_url = self.portal.absolute_url() + '/test-form-result'

    @browsing
    def test_get_request(self, browser):
        browser.open(self.portal.portal_url())
        self.assertEquals(self.portal.portal_url(), browser.url)

    @browsing
    def test_open_with_view_only(self, browser):
        browser.open(view='login_form')
        self.assertEquals(self.portal.portal_url() + '/login_form', browser.url)

    @browsing
    def test_open_site_root_by_default(self, browser):
        browser.open()
        self.assertEquals(self.portal.portal_url(), browser.url)

    @browsing
    def test_post_request(self, browser):
        browser.open(self.portal.portal_url() + '/login_form')
        self.assertFalse(plone.logged_in())

        browser.open(self.portal.portal_url() + '/login_form',
                     {'__ac_name': TEST_USER_NAME,
                      '__ac_password': TEST_USER_PASSWORD,
                      'form.submitted': 1})
        self.assertTrue(plone.logged_in())

    @browsing
    def test_post_request_with_umlauts(self, browser):
        browser.open(view='test-form-result', data={u'Uml\xe4ute': u'Uml\xe4ute'})
        self.assertEquals({u'Uml\xe4ute': u'Uml\xe4ute'}, browser.json)

    @skip_driver(LIB_REQUESTS, 'Exception bubbling is not supported.')
    @browsing
    def test_support_exception_bubbling(self, browser):
        class FailingView(BrowserView):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(FailingView, 'failing-view'):
            # Excpect reguler HTTP error by default since the value error
            # is rendered by Zope as a 500.
            with browser.expect_http_error(code=500):
                browser.open(view='failing-view')

            # When exception bubbling is enabled we should be able to catch
            # the value error from the rendered view.
            browser.exception_bubbling = True
            with self.assertRaises(ValueError) as cm:
                browser.open(view='failing-view')

            self.assertEquals('The value is wrong.', str(cm.exception))

    @skip_driver(LIB_MECHANIZE, 'Exception bubbling is supported.')
    @browsing
    def test_unsupport_exception_bubbling(self, browser):
        browser.exception_bubbling = True
        with self.assertRaises(ValueError) as cm:
            browser.open()

        self.assertEquals(
            'The requests driver does not support exception bubbling.',
            str(cm.exception))

    @browsing
    def test_visit_object(self, browser):
        folder = create(Builder('folder').titled(u'Test Folder'))
        browser.login().visit(folder)
        self.assertEquals(self.portal.portal_url() + '/test-folder', browser.url)

    @browsing
    def test_visit_view_on_object(self, browser):
        folder = create(Builder('folder').titled(u'Test Folder'))
        browser.login().visit(folder, view='folder_contents')
        self.assertEquals(
            self.portal.portal_url() + '/test-folder/folder_contents',
            browser.url)

    @browsing
    def test_on_opens_a_page(self, browser):
        browser.on(view='login_form')
        self.assertEquals('login_form', browser.url.split('/')[-1])

    @browsing
    def test_on_changes_page_when_necessary(self, browser):
        browser.open()
        self.assertEquals('plone', browser.url.split('/')[-1])
        browser.on(view='login_form')
        self.assertEquals('login_form', browser.url.split('/')[-1])

    @browsing
    def test_on_does_not_reload_when_already_on_this_page(self, browser):
        # Not reloading the page also means not resetting the state of the
        # document - that means for example that filled form field values
        # are not reset.
        # We use this behavior in this test, since it is an easy we to test
        # whether there was a request invoked or not.

        browser.open(view='login_form')
        browser.fill({'Login Name': 'userid'})
        self.assertDictContainsSubset(
            {'__ac_name': 'userid'},
            dict(browser.forms['login_form'].values))

        browser.on(view='login_form')
        self.assertDictContainsSubset(
            {'__ac_name': 'userid'},
            dict(browser.forms['login_form'].values),
            'Seems that the page was reloaded when using browser.on'
            ' even though we are already on this page.')

    @browsing
    def test_loading_string_html_without_request(self, browser):
        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '<html>'))

        browser.open_html(html)
        self.assertEquals('The heading', browser.css('h1').first.normalized_text())

    @browsing
    def test_loading_stream_html_without_request(self, browser):
        html = StringIO()
        html.write('<html>')
        html.write('<h1>The heading</h1>')
        html.write('<html>')

        browser.open_html(html)
        self.assertEquals('The heading', browser.css('h1').first.normalized_text())

    @browsing
    def test_open_html_sets_response_to_html_stream(self, browser):
        """
        When an exception happens within a test, the response content is dumped
        to a temporary file for debugging purpose.
        In order for that to work, browser.contents must be the HTML body.
        """

        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '<html>'))

        browser.open_html(html)
        self.assertEquals(html, browser.contents)

    @browsing
    def test_logout_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_relogin_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        john = create(Builder('user').named('John', 'Doe'))
        browser.login(john.getId()).open()
        self.assertEquals('Doe John', plone.logged_in())

    @browsing
    def test_login_with_member_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the member object.
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        browser.login(member).open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_login_with_user_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the user object.
        acl_users = getToolByName(self.layer['portal'], 'acl_users')
        user = acl_users.getUserById(TEST_USER_ID)
        browser.login(user).open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_append_request_header(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.open()  # reload
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_x_zope_handle_errors_header_is_forbidden(self, browser):
        with self.assertRaises(ValueError) as cm:
            browser.append_request_header('X-zope-handle-errors', 'False')

        self.assertEquals(
            'The testbrowser does no longer allow to set the request header '
            '\'X-zope-handle-errros\'; use the exception_bubbling flag instead.',
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            browser.clear_request_header('X-zope-handle-errors')

    @browsing
    def test_replace_request_header(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        john = create(Builder('user').named('John', 'Doe'))

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((hugo.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        browser.replace_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((john.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Doe John', plone.logged_in())

    @browsing
    def test_clear_request_header_with_header_selection(self, browser):
        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.clear_request_header('Authorization')
        browser.open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_reload_GET_request(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': 'the-user-id'})
        self.assertDictContainsSubset(
            {'__ac_name': 'the-user-id'},
            dict(browser.forms['login_form'].values))

        browser.reload()
        self.assertDictContainsSubset(
            {'__ac_name': ''},
            dict(browser.forms['login_form'].values))

    @browsing
    def test_reload_POST_reqest(self, browser):
        browser.visit(view='test-form')
        browser.fill({'Text field': 'Some Value'}).submit()
        self.assertDictContainsSubset({'textfield': 'Some Value'}, browser.json)
        browser.reload()
        self.assertDictContainsSubset({'textfield': 'Some Value'}, browser.json)

    @browsing
    def test_reload_when_not_viewing_a_page(self, browser):
        with self.assertRaises(BlankPage) as cm:
            browser.reload()
        self.assertEquals('The browser is on a blank page. Cannot reload.',
                          str(cm.exception))

    @browsing
    def test_fill_and_submit_multi_select_form(self, browser):
        browser.open()
        browser.parse(
            '\n'.join(('<form action="{0}">'.format(self.json_view_url),
                       '<select name="selectfield" multiple="multiple">',
                       '<option>Foo</option>',
                       '<option>Bar</option>',
                       '<option>Baz</option>',
                       '</select>')))
        browser.fill({'selectfield': ['Foo', 'Baz']}).submit()
        self.assertDictContainsSubset(
            {u'selectfield': [u'Foo', u'Baz']},
            browser.json)

    @browsing
    def test_support_multi_value_data_as_dict_with_list_values(self, browser):
        browser.open(self.json_view_url, data={'values': ['Foo', 'Bar']})
        self.assertDictContainsSubset(
            {u'values': [u'Foo', u'Bar']},
            browser.json)

    @browsing
    def test_support_multi_value_data_as_list_with_tuples(self, browser):
        browser.open(self.json_view_url, data=[('values', 'Foo'),
                                               ('values', 'Bar')])
        self.assertDictContainsSubset(
            {u'values': [u'Foo', u'Bar']},
            browser.json)

    @browsing
    def test_response_contenttype(self, browser):
        browser.open()
        self.assertIn(browser.contenttype,
                      ('text/html;charset=utf-8',
                       'text/html; charset=utf-8'))

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEquals('application/json', browser.contenttype)

    @browsing
    def test_response_mimetype(self, browser):
        browser.open()
        self.assertEquals('text/html', browser.mimetype)

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEquals('application/json', browser.mimetype)

    @browsing
    def test_response_encoding(self, browser):
        browser.open()
        self.assertEquals('utf-8', browser.encoding)

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEquals(None, browser.encoding)

    @browsing
    def test_keeps_cookies_in_session(self, browser):
        browser.open(view='login_form')
        self.assertEquals(0, len(browser.cookies))

        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertIn('__ac', browser.cookies)
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.open()
        self.assertIn('__ac', browser.cookies)
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.open()
        self.assertIn('__ac', browser.cookies)
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_login_and_logout(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.login().open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())
