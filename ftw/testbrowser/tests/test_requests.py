from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.core import LIB_TRAVERSAL
from ftw.testbrowser.core import LIB_WEBTEST
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import RedirectLoopException
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests import IS_PLONE_4
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver
from ftw.testbrowser.tests.helpers import register_view
from ftw.testbrowser.utils import basic_auth_encode
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from six import BytesIO
from unittest import skipUnless
from zExceptions import BadRequest
from zope.component import getUtility
from zope.publisher.browser import BrowserView


LOGIN_FORM_ID = 'login_form'
if getFSVersionTuple() >= (5, 2):
    LOGIN_FORM_ID = 'form-1'


@all_drivers
class TestBrowserRequests(BrowserTestCase):

    def setUp(self):
        super(TestBrowserRequests, self).setUp()
        self.grant('Manager')
        self.json_view_url = self.portal.absolute_url() + '/test-form-result'

    @browsing
    def test_get_request(self, browser):
        browser.open(self.portal.portal_url())
        self.assertEqual(self.portal.portal_url(), browser.url)

    @browsing
    def test_open_with_view_only(self, browser):
        browser.open(view='login_form')
        self.assertEqual(self.portal.portal_url() + '/login_form', browser.url)

    @browsing
    def test_open_site_root_by_default(self, browser):
        browser.open()
        self.assertEqual(self.portal.portal_url(), browser.url)

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
        self.assertEqual({u'Uml\xe4ute': u'Uml\xe4ute'}, browser.json)

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

            self.assertEqual('The value is wrong.', str(cm.exception))

    @skip_driver(LIB_MECHANIZE, 'Exception bubbling is supported by mechanize.')
    @skip_driver(LIB_TRAVERSAL, 'Exception bubbling is supported by traversal.')
    @skip_driver(LIB_WEBTEST, 'Exception bubbling is supported by webtest.')
    @browsing
    def test_unsupport_exception_bubbling(self, browser):
        browser.exception_bubbling = True
        with self.assertRaises(ValueError) as cm:
            browser.open()

        self.assertEqual(
            'The requests driver does not support exception bubbling.',
            str(cm.exception))

    @browsing
    def test_visit_object(self, browser):
        folder = create(Builder('folder').titled(u'Test Folder'))
        browser.login().visit(folder)
        self.assertEqual(self.portal.portal_url() + '/test-folder', browser.url)

    @browsing
    def test_visit_view_on_object(self, browser):
        folder = create(Builder('folder').titled(u'Test Folder'))
        browser.login().visit(folder, view='folder_contents')
        self.assertEqual(
            self.portal.portal_url() + '/test-folder/folder_contents',
            browser.url)

    @browsing
    def test_on_opens_a_page(self, browser):
        browser.on(view='login_form')
        self.assertEqual('login_form', browser.url.split('/')[-1])

    @browsing
    def test_on_changes_page_when_necessary(self, browser):
        browser.open()
        self.assertEqual('plone', browser.url.split('/')[-1])
        browser.on(view='login_form')
        self.assertEqual('login_form', browser.url.split('/')[-1])

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
            dict(browser.forms[LOGIN_FORM_ID].values))

        browser.on(view='login_form')
        self.assertDictContainsSubset(
            {'__ac_name': 'userid'},
            dict(browser.forms[LOGIN_FORM_ID].values),
            'Seems that the page was reloaded when using browser.on'
            ' even though we are already on this page.')

    @browsing
    def test_loading_string_html_without_request(self, browser):
        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '<html>'))

        browser.open_html(html)
        self.assertEqual('The heading', browser.css('h1').first.normalized_text())

    @browsing
    def test_loading_stream_html_without_request(self, browser):
        html = BytesIO()
        html.write(b'<html>')
        html.write(b'<h1>The heading</h1>')
        html.write(b'<html>')

        browser.open_html(html)
        self.assertEqual('The heading', browser.css('h1').first.normalized_text())

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
        self.assertEqual(html, browser.contents)

    @browsing
    def test_logout_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEqual('Boss Hugo', plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_relogin_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEqual('Boss Hugo', plone.logged_in())

        john = create(Builder('user').named('John', 'Doe'))
        browser.login(john.getId()).open()
        self.assertEqual('Doe John', plone.logged_in())

    @browsing
    def test_login_with_member_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the member object.
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        browser.login(member).open()
        self.assertEqual(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_login_with_user_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the user object.
        acl_users = getToolByName(self.layer['portal'], 'acl_users')
        user = acl_users.getUserById(TEST_USER_ID)
        browser.login(user).open()
        self.assertEqual(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_append_request_header(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.append_request_header(
            'Authorization',
            basic_auth_encode(TEST_USER_NAME, TEST_USER_PASSWORD))
        browser.open()
        self.assertEqual(TEST_USER_ID, plone.logged_in())

        browser.open()  # reload
        self.assertEqual(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_x_zope_handle_errors_header_is_forbidden(self, browser):
        with self.assertRaises(ValueError) as cm:
            browser.append_request_header('X-zope-handle-errors', 'False')

        self.assertEqual(
            'The testbrowser does no longer allow to set the request header '
            '\'X-zope-handle-errros\'; use the exception_bubbling flag instead.',
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            browser.clear_request_header('X-zope-handle-errors')

    @browsing
    def test_replace_request_header(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        john = create(Builder('user').named('John', 'Doe'))

        browser.append_request_header(
            'Authorization',
            basic_auth_encode(hugo.getId(), TEST_USER_PASSWORD))
        browser.open()
        self.assertEqual('Boss Hugo', plone.logged_in())

        browser.replace_request_header(
            'Authorization',
            basic_auth_encode(john.getId(), TEST_USER_PASSWORD))
        browser.open()
        self.assertEqual('Doe John', plone.logged_in())

    @browsing
    def test_clear_request_header_with_header_selection(self, browser):
        browser.append_request_header(
            'Authorization',
            basic_auth_encode(TEST_USER_NAME, TEST_USER_PASSWORD))
        browser.open()
        self.assertEqual(TEST_USER_ID, plone.logged_in())

        browser.clear_request_header('Authorization')
        browser.open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_reload_GET_request(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': 'the-user-id'})
        self.assertDictContainsSubset(
            {'__ac_name': 'the-user-id'},
            dict(browser.forms[LOGIN_FORM_ID].values))

        browser.reload()
        self.assertDictContainsSubset(
            {'__ac_name': ''},
            dict(browser.forms[LOGIN_FORM_ID].values))

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
        self.assertEqual('The browser is on a blank page. Cannot reload.',
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
        # Plone 4: utf-8
        # Plone 5 UTF-8
        self.assertIn(browser.contenttype.lower(),
                      ('text/html;charset=utf-8',
                       'text/html; charset=utf-8'))

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEqual('application/json', browser.contenttype)

    @browsing
    def test_response_mimetype(self, browser):
        browser.open()
        self.assertEqual('text/html', browser.mimetype)

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEqual('application/json', browser.mimetype)

    @browsing
    def test_response_encoding(self, browser):
        browser.open()
        # Plone 4: utf-8
        # Plone 5 UTF-8
        self.assertEqual('utf-8', browser.encoding.lower())

        browser.open(self.json_view_url, data={'foo': 'bar'})
        self.assertEqual(None, browser.encoding)

    @browsing
    def test_keeps_cookies_in_session(self, browser):
        browser.open(view='login_form')
        self.assertEqual(0, len(browser.cookies))

        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertIn('__ac', browser.cookies)
        self.assertEqual(TEST_USER_ID, plone.logged_in())

        browser.open()
        self.assertIn('__ac', browser.cookies)
        self.assertEqual(TEST_USER_ID, plone.logged_in())

        browser.open()
        self.assertIn('__ac', browser.cookies)
        self.assertEqual(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_login_and_logout(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.login().open()
        self.assertEqual(TEST_USER_ID, plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_redirects_are_followed_automatically(self, browser):
        browser.open(view='test-redirect-to-portal')
        self.assertEqual(self.portal.absolute_url(), browser.url)
        self.assertEqual(('listing_view', 'plone-site'),
                         plone.view_and_portal_type())

    @skip_driver(LIB_MECHANIZE, 'Changing redirect following behavior is not supported.')
    @browsing
    def test_redirect_following_can_be_prevented(self, browser):
        browser.allow_redirects = False
        browser.open(view='test-redirect-to-portal')
        self.assertEqual('/'.join((self.portal.absolute_url(), 'test-redirect-to-portal')), browser.url)
        self.assertEqual((None, None), plone.view_and_portal_type())

    @browsing
    def test_redirect_loops_are_interrupted(self, browser):
        with self.assertRaises(RedirectLoopException) as cm:
            browser.open(view='test-redirect-loop')

        self.assertEqual(
            'The server returned a redirect response that would lead'
            ' to an infinite redirect loop.\n'
            'URL: {}/test-redirect-loop'.format(self.portal.absolute_url()),
            str(cm.exception))

    @skipUnless(IS_PLONE_4, 'gzip compression was removed in Plone 5.')
    @browsing
    def test_decompresses_gzip_responses(self, browser):
        browser.login().open()
        self.assertEqual('<!DOCTYPE', browser.contents.strip()[:9])

        # Install plone.app.caching in order to enable compression:
        applyProfile(self.portal, 'plone.app.caching:default')
        applyProfile(self.portal, 'plone.app.caching:without-caching-proxy')
        getUtility(IRegistry)['plone.app.caching.interfaces'
                              '.IPloneCacheSettings.enableCompression'] = True
        self.maybe_commit_transaction()

        browser.reload()
        if browser.get_driver().LIBRARY_NAME != LIB_REQUESTS:
            self.assertEqual(None, browser.headers.get('content-encoding'),
                             'The content-encoding header should be removed'
                             ' in order to indicate that the content is now'
                             ' unzipped.')

        self.assertEqual('<!DOCTYPE', browser.contents.strip()[:9])

    @browsing
    def test_partial_template_encoding_utf8(self, browser):
        """Plone may choose a different encoding (such as ISO-8859-15) when there is
        neither an encoding specificed in the response header nor in an xml node.
        The testbrowser must then adapt and use the correct encoding.
        """
        browser.open(view='test-partial?set_utf8_encoding=True')
        self.assertEqual('utf-8', browser.encoding.lower())
        self.assertEqual([u'Bj\xf6rn', u'G\xfcnther', u'A\xefda'],
                         browser.css('#names li').text)

    @browsing
    def test_partial_template_encoding_latin9(self, browser):
        """Plone may choose a different encoding (such as ISO-8859-15) when there is
        neither an encoding specificed in the response header nor in an xml node.
        The testbrowser must then adapt and use the correct encoding.
        """
        browser.open(view='test-partial')

        default_encoding = 'iso-8859-15'
        # Plone 5.1.6 (plone.testing 4.3.3) sets ZPublisher encoding to UTF-8
        if getFSVersionTuple() >= (5, 1, 6):
            default_encoding = 'utf-8'

        self.assertEqual(default_encoding, browser.encoding.lower())
        self.assertEqual([u'Bj\xf6rn', u'G\xfcnther', u'A\xefda'],
                         browser.css('#names li').text)

    @browsing
    def test_send_authenticator(self, browser):
        class ProtectedView(BrowserView):
            def __call__(self):
                if not self.context.restrictedTraverse('@@authenticator').verify():
                    raise BadRequest('No way sir')
                else:
                    return 'YAY'

        with register_view(ProtectedView, 'protected-view'):
            browser.login()

            # Fails when no authenticator token is provided:
            with browser.expect_http_error(code=400):
                browser.open(view='protected-view')

            # But we can tell the browser to send the authenticator token:
            browser.open(view='protected-view', send_authenticator=True)
            self.assertEqual('YAY', browser.contents)
