
==============
 Introduction
==============

.. contents:: :local:


`ftw.testbrowser` is a browser library for testing `Plone`_ based web sites
and applications (CI).


Features
========

The test browser supports all the basic features:

- Visit pages of the Plone site
- Access page content
- Find nodes by CSS- and XPath-Expressions or by text
- Click on links
- Fill and submit forms
- File uploading
- Make WebDAV requests

The `ftw.testbrowser` also comes with some basic Plone
`page objects <http://martinfowler.com/bliki/PageObject.html>`_.

`ftw.testbrowser` currently does not support JavaScript.


Motivation
==========

A test browser should have a simple but powerful API (CSS expressions), it should
be fast, reliable and easy to setup and use.

The existing test browsers for Plone development were not satisfactory:

- The `zope.testbrowser <https://pypi.python.org/pypi/zope.testbrowser>`_, which
  is the current standard for Plone testing does not support CSS- or XPath-Selectors,
  it is very limiting in form filling (buttons without names are not selectable, for
  example) and it leads to brittle tests.

- The `splinter <https://pypi.python.org/pypi/splinter>`_ test browser has a zope
  driver and various selenium based drivers. This abstraction improves the
  API but it is still limiting since it bases on `zope.testbrowser`.

- The `robotframework <https://pypi.python.org/pypi/robotframework>`_ is a selenium
  based full-stack browser which comes with an own language and requires a huge setup.
  The use of selenium makes it slow and brittle and a new language needs to be learned.

There are also some more browser libraries and wrappers, usually around selenium, which
often requires to open a port and make actual requests. This behavior is very time
consuming and should not be done unless really necessary, which is usally for visual
things (making screenshots) and JavaScript testing.


How it works
============

The `ftw.testbrowser` uses `mechanize`_ with `plone.testing`_ configurations / patches
to directly dispatch requests in Zope.

The responses are parsed in an `lxml`_.html document, which allows us to do all the
necessary things such as selecting HTML elements or filling forms.

While querying, `ftw.testbrowser` wraps all the HTML elements into node wrappers which
extend the `lxml` functionality with things such as using `CSS` selectors directly,
clicking on links or filling forms based on labels.



.. _Plone: http://www.plone.org/
.. _lxml: http://lxml.de/
.. _mechanize: https://pypi.python.org/pypi/mechanize
.. _plone.testing: https://pypi.python.org/pypi/plone.testing
