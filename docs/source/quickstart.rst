============
 Quickstart
============

Add `ftw.testbrowser` to your testing dependencies in your `setup.py`:

.. code:: py

    tests_require = [
        'ftw.testbrowser',
        ]

    setup(name='my.package',
          install_requires=['Plone'],
          tests_require=tests_require,
          extras_require=dict(tests=tests_require))

Write tests using the browser:

.. code:: py

    from ftw.testbrowser import browsing
    from ftw.testbrowser.pages import factoriesmenu
    from ftw.testbrowser.pages import plone
    from ftw.testbrowser.pages import statusmessages
    from plone.app.testing import PLONE_FUNCTIONAL_TESTING
    from plone.app.testing import SITE_OWNER_NAME
    from unittest2 import TestCase


    class TestFolders(TestCase):

        layer = PLONE_FUNCTIONAL_TESTING

        @browsing
        def test_add_folder(self, browser):
            browser.login(SITE_OWNER_NAME).open()
            factoriesmenu.add('Folder')
            browser.fill({'Title': 'The Folder'}).submit()

            statusmessages.assert_no_error_messages()
            self.assertEquals('folder_listing', plone.view())
            self.assertEquals('The Folder', plone.first_heading())
