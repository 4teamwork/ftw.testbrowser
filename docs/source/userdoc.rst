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
