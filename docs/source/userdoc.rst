====================
 User documentation
====================

.. contents:: :local:


Setup
=====

For using the test browser, just decorate your test methods with the `@browsing`
decorator.


.. code:: py

    from ftw.testbrowser import browsing
    from unittest2 import TestCase
    from plone.app.testing import PLONE_FUNCTIONAL_TESTING


    class TestMyView(TestCase):

        layer = PLONE_FUNCTIONAL_TESTING

        @browsing
        def test_view_displays_things(self, browser):
            browser.visit(view='my_view')

.. warning:: Make sure that you use a functional testing layer!
.. seealso:: :py:func:`ftw.testbrowser.browsing`

By default there is only one, global browser, but it is also possible to instantiate
a new browser and to set it up manually:

.. code:: py

    from ftw.testbrowser.core import Browser

    browser = Browser()
    app = zope_app

    with browser(app):
        browser.open()

.. warning:: Page objects and forms usually use the global browser. Creating a new
   browser manually will not set it as global browser and page objects / forms will
   not be able to access it!

Choosing the default driver
---------------------------

The default driver is chosen automatically, depending on whether the browser is
set up with a zope app (=> ``LIB_MECHANIZE``) or not (=> ``LIB_REQUESTS``).
The default driver can be changed on the browser instance, overriding the
automatic driver selection:

.. code:: py

    from ftw.testbrowser.core import Browser
    from ftw.testbrowser.core import LIB_MECHANIZE
    from ftw.testbrowser.core import LIB_REQUESTS
    from ftw.testbrowser.core import LIB_TRAVERSAL

    browser = Browser()
    # always use mechanize:
    browser.default_driver = LIB_MECHANIZE

    # or always use requests:
    browser.default_driver = LIB_REQUESTS

    # or use traversal in the same transactions with same connection:
    browser.default_driver = LIB_TRAVERSAL


When using the testbrowser in a ``plone.testing`` layer, the driver can be
chosen by using a standard ``plone.testing`` fixture:

.. code:: py

    from ftw.testbrowser import MECHANIZE_BROWSER_FIXTURE
    from ftw.testbrowser import REQUESTS_BROWSER_FIXTURE
    from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
    from plone.app.testing import PLONE_FIXTURE
    from plone.app.testing import FunctionalTesting


    MY_FUNCTIONAL_TESTING_WITH_MECHANIZE = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               MECHANIZE_BROWSER_FIXTURE),
        name='functional:mechanize')

    MY_FUNCTIONAL_TESTING_WITH_REQUESTS = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               REQUESTS_BROWSER_FIXTURE),
        name='functional:requests')

    MY_FUNCTIONAL_TESTING_WITH_TRAVERSAL = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               TRAVERSAL_BROWSER_FIXTURE),
        name='functional:traversal')




Visit pages
===========

For visiting a page, use the `visit` or `open` method on the browser (those methods
do the same).

Visiting the Plone site root:

.. code:: py

    browser.open()
    print browser.url

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.url`

Visiting a full url:

.. code:: py

    browser.open('http://nohost/plone/sitemap')

Visiting an object:

.. code:: py

    folder = portal.get('the-folder')
    browser.visit(folder)

Visit a view on an object:

.. code:: py

    folder = portal.get('the-folder')
    browser.visit(folder, view='folder_contents')

The `open` method can also be used to make POST request:

.. code:: py

    browser.open('http://nohost/plone/login_form',
                 {'__ac_name': TEST_USER_NAME,
                  '__ac_password': TEST_USER_PASSWORD,
                  'form.submitted': 1})


.. seealso:: :py:func:`ftw.testbrowser.core.Browser.open`


Logging in
==========

The `login` method sets the `Authorization` request header.

Login with the `plone.app.testing` default test user (`TEST_USER_NAME`):

.. code:: py

    browser.login().open()

Logging in with another user:

.. code:: py

    browser.login(username='john.doe', password='secret')

Logout and login a different user:

.. code:: py

    browser.login(username='john.doe', password='secret').open()
    browser.reset()
    browser.login().open()


.. seealso:: :py:func:`ftw.testbrowser.core.Browser.login`,
             :py:func:`ftw.testbrowser.core.Browser.reset`


Finding elements
================

Elements can be found using CSS-Selectors (`css` method) or using XPath-Expressions
(`xpath` method). A result set (`Nodes`) of all matches is returned.

.. seealso:: :py:func:`ftw.testbrowser.nodes.Nodes`


CSS:

.. code:: py

    browser.open()
    heading = browser.css('.documentFirstHeading').first
    self.assertEquals('Plone Site', heading.normalized_text())

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.css`,
             :py:func:`ftw.testbrowser.nodes.NodeWrapper.normalized_text`


XPath:

.. code:: py

    browser.open()
    heading = browser.xpath('h1').first
    self.assertEquals('Plone Site', heading.normalized_text())


.. seealso:: :py:func:`ftw.testbrowser.core.Browser.xpath`


Finding elements by text:

.. code:: py

    browser.open()
    browser.find('Sitemap').click()

The `find` method will look for theese elements (in this order):

- a link with this text (normalized, including subelements' texts)
- a field which has a label with this text
- a button which has a label with this text


.. seealso:: :py:func:`ftw.testbrowser.core.Browser.find`


Matching text content
=====================

In HTML, most elements can contain direct text but the elements can also
contain sub-elements which also have text.

When having this HTML:

.. code:: html

    <a id="link">
        This is
        <b>a link
    </a>

We can get only direct text of the link:

.. code:: py

    >>> browser.css('#link').first.text
    '\n        This is\n        '

or the text recursively:

.. code:: py

    >>> browser.css('#link').first.text_content()
    '\n        This is\n        a link\n    '

.. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.text_content`

or the normalized recursive text:

.. code:: py

    >>> browser.css('#link').first.normalized_text()
    'This is a link'

.. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.normalized_text`

Functions such as `find` usually use the `normalized_text`.

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.find`


Get the page contents / json data
=================================

The page content of the currently loaded page is always available on the browser:

.. code :: py

    browser.open()
    print browser.contents

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.contents`

If the result is a JSON string, you can access the JSON data (converted to python
data structure already) with the `json` property:

.. code :: py

    browser.open(view='a-json-view')
    print browser.json

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.json`


Filling and submitting forms
============================

The browser's `fill` method helps to easily fill forms by label text without knowing
the structure and details of the form:

.. code:: py

    browser.visit(view='login_form')
    browser.fill({'Login Name': TEST_USER_NAME,
                  'Password': TEST_USER_PASSWORD}).submit()

The `fill` method returns the browser instance which can be submitted with `submit`.
The keys of the dict with the form data can be either field labels (`<label>` text) or
the name of the field. Only one form can be filled at a time.


File uploading
--------------

For uploading a file you need to pass at least the file data (string or stream) and
the filename to the `fill` method, optionally you can also declare a mime type.

There are two syntaxes which can be used.

**Tuple syntax:**

.. code:: py

    browser.fill({'File': ('Raw file data', 'file.txt', 'text/plain')})

**Stream syntax**

.. code:: py

    file_ = StringIO('Raw file data')
    file_.filename = 'file.txt'
    file_.content_type = 'text/plain'

    browser.fill({'File': file_})

You can also pass in filesystem files directly, but you need to make sure that the
file stream is opened untill the form is submitted.

.. code:: py

    with open('myfile.pdf') as file_:
        browser.fill({'File': file_}).submit()


.. seealso:: :py:func:`ftw.testbrowser.core.Browser.fill`,
             :py:func:`ftw.testbrowser.form.Form.submit`,
             :py:func:`ftw.testbrowser.form.Form.save`


Tables
======

Tables are difficult to test without the right tools.
For making the tests easy and readable, the table components provide helpers
especially for easily extracting a table in a readable form.

For testing the content of this table:

.. code:: html

            <table id="shopping-cart">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Socks</td>
                        <td>12.90</td>
                    </tr>
                    <tr>
                        <td>Pants</td>
                        <td>35.00</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <td>TOTAL:</td>
                        <td>47.90</td>
                    </tr>
                </tfoot>
            </table>

You could use the ``lists`` method:

.. code:: py

    self.assertEquals(
        [['Product', 'Price'],
         ['Socks', '12.90'],
         ['Pants', '35.00'],
         ['TOTAL:', '47.90']],
        browser.css('#shopping-cart').first.lists())

.. seealso:: :py:func:`ftw.testbrowser.table.Table.lists`

or the ``dicts`` method:

.. code:: py

    self.assertEquals(
        [{'Product': 'Socks',
          'Price': '12.90'},
         {'Product': 'Pants',
          'Price': '35.00'},
         {'Product': 'TOTAL:',
          'Price': '47.90'}],
        browser.css('#shopping-cart').first.dicts())

.. seealso:: :py:func:`ftw.testbrowser.table.Table.dicts`

See the tables API for more details.

.. seealso:: :py:func:`ftw.testbrowser.table.Table`,
             :py:func:`ftw.testbrowser.table.TableRow`,
             :py:func:`ftw.testbrowser.table.TableCell`


Page objects
============

`ftw.testbrowser` ships some basic page objects for Plone.
Page objects represent a page or a part of a page and provide an API to this part.
This allows us to write simpler and more expressive tests and makes the tests less
brittle.

Read the `post by Martin Fowler <http://martinfowler.com/bliki/PageObject.html>`_
for better explenation about what page objects are.

You can and should write your own page objects for your views and pages.

See the API documentation for the page objects included in `ftw.testbrowser`:

- The **plone** page object provides general information about this page, such as
  if the user is logged in or the view / portal type of the page.

- The **factoriesmenu** page object helps to add new content through the browser or
  to test the addable types.

- The **statusmessages** page object helps to assert the current status messages.

- The **dexterity** page object provides helpers related to dexterity

- The **z3cform** page object provides helpers related to z3cforms, e.g. for asserting
  validation errors in the form.

.. seealso:: :py:mod:`ftw.testbrowser.pages`


XML Support
===========

When the response mimetype is ``text/xml`` or ``application/xml``, the response body is
parsed as XML instead of HTML.

This can lead to problems when having XML-Documents with a default namespace,
because lxml only supports XPath 1, which does not support default namespaces.

You can either solve the problem yourself by parsing the ``browser.contents`` or you
may switch back to HTML parsing.
HTML parsing will modify your document though, it will insert a ``html`` node for example.

Re-parsing with another parser:

.. code:: py

    browser.webdav(view='something.xml')  # XML document
    browser.parse_as_html()               # HTML document
    browser.parse_as_xml()                # XML document


.. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_html`
.. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_xml`
.. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse`


WebDAV requests
===============

`ftw.testbrowser` supports doing WebDAV requests, although it requires a
ZServer to be running because of limitations in mechanize.

Use a testing layer which bases on ``plone.app.testing.PLONE_ZSERVER``:

.. code:: py

    from plone.app.testing import FunctionalTesting
    from plone.app.testing import PLONE_FIXTURE
    from plone.app.testing import PLONE_ZSERVER
    from plone.app.testing import PloneSandboxLayer


    class MyPackageLayer(PloneSandboxLayer):

        defaultBases = (PLONE_FIXTURE, )

    MY_PACKAGE_FIXTURE = MyPackageLayer()
    MY_PACKAGE_ZSERVER_TESTING = FunctionalTesting(
        bases=(MY_PACKAGE_FIXTURE,
               PLONE_ZSERVER),
        name='my.package:functional:zserver')

Then use the ``webdav`` method for making requests in the test:

.. code:: py

    from ftw.testbrowser import browsing
    from my.package.testing import MY_PACKAGE_ZSERVER_TESTING
    from unittest2 import TestCase


    class TestWebdav(TestCase):

        layer = MY_PACKAGE_ZSERVER_TESTING

        @browsing
        def test_DAV_option(self, browser):
            browser.webdav('OPTIONS')
            self.assertEquals('1,2', browser.response.headers.get('DAV'))

.. seealso:: :py:func:`ftw.testbrowser.core.Browser.webdav`


Error handling
==============

The testbrowser raises exceptions by default when a request was not successful.
When the response has a status code of `4xx`, a
:py:class:`ftw.testbrowser.exceptions.HTTPClientError` is raised,
when the status code is `5xx`, a
:py:class:`ftw.testbrowser.exceptions.HTTPServerError` is raised.


Disabling HTTP exceptions
-------------------------

Disable the ``raise_http_errors`` flag when the test browser should not raise
any HTTP exceptions:

.. code::

   @browsing
   def test(self, browser):
       browser.raise_http_errors = False
       browser.open(view='not-existing')


Expecting HTTP exceptions
-------------------------

Sometimes we want to make sure that the server responds with a certain bad
status. For making that easy, the testbrowser provides assertion context
managers:


.. code::

   @browsing
   def test(self, browser):
       with browser.expect_http_error():
           browser.open(view='failing')

       with browser.expect_http_error(code=404):
           browser.open(view='not-existing')

       with browser.expect_http_error(reason='Bad Request'):
           browser.open(view='get-record-by-id')


Expecting unauthoirzed exceptions (Plone)
-----------------------------------------

When a user is not logged in and is not authorized to access a resource,
Plone will redirect the user to the login form (``require_login``).
The ``expect_unauthorized`` context manager knows how Plone behaves and provides
an easy interface so that the developer does not need to handle it.

.. code::

    @browsing
    def test(self, browser):
        with browser.expect_unauthorized():
            browser.open(view='plone_control_panel')



Exception bubbling
------------------

Exceptions happening in views can not be catched in the browser by default.
When using an internally dispatched driver such as Mechanize,
the option ``exception_bubbling`` makes the Zope Publisher and Mechanize
let the exceptions bubble up into the test method, so that it can be catched
and asserted there.

.. code::

   @browsing
   def test(self, browser):
       browser.exception_bubbling = True
       with self.assertRaises(ValueError) as cm:
           browser.open(view='failing')

       self.assertEquals('No valid value was submitted', str(cm.exception))
