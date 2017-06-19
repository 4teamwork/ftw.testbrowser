Changelog
=========


1.24.1 (2017-06-19)
-------------------

- Declare missing dependencies. [lgraf]


1.24.0 (2017-06-16)
-------------------

- Log exceptions to stderr when they are not expected. [jone]
- Standardize redirect loop detection: always throw a ``RedirectLoopException``. [jone]
- Add traversal request driver. [jone]


1.23.2 (2017-06-16)
-------------------

- Fix `browser.context` when base_url ends with a view name. [phgross]


1.23.1 (2017-05-02)
-------------------

- Fix `browser.debug` when body is a bytestring. [jone]


1.23.0 (2017-04-28)
-------------------

- Introduce ``browser.expect_unauthorized`` context manager. [jone]


1.22.2 (2017-04-28)
-------------------

- HTTPError: include code and reason in exception. [jone]
- Docs: Fix wrong expect_http_error argument names. [jone]


1.22.1 (2017-04-28)
-------------------

- Docs: swith to RTD, update URLs. [jone]
- Docs: Switch to RTD Sphinx theme. [lgraf]


1.22.0 (2017-04-28)
-------------------

- Forbid setting of "x-zope-handle-errors" header. [jone]
- Add an option ``browser.exception_bubbling``, disabled by default. [jone]
- Mechanize: no longer disable "x-zope-handle-errors". [jone]
- Introduce ``browser.expect_http_error()`` context manager. [jone]
- Add an option ``browser.raise_http_errors``, enabled by default. [jone]
- Raise ``HTTPClientError`` and ``HTTPServerError`` by default. [jone]
- Introduce ``browser.status_reason``. [jone]
- Introduce ``browser.status_code``. [jone]


1.21.0 (2017-04-19)
-------------------

- Make ``zope.globalrequest`` support optional. [jone]
- Add testing layers for setting the default driver. [jone]
- Add ``default_driver`` option to the driver. [jone]
- Refactoring: introduce request drivers. [jone]


1.20.0 (2017-04-10)
-------------------

- Add Support for Button tag. [tschanzt]
- No longer test with Archetypes, test only with dexterity. [jone]
- Support latest Plone 4.3.x release. [mathias.leimgruber]


1.19.3 (2016-07-25)
-------------------

- Declare some previously missing test requirements.
  [lgraf]

- Declare previously missing dependency on zope.globalrequest (introduced in #35).
  [lgraf]


1.19.2 (2016-06-27)
-------------------

- Preserve the request of zope.globalrequest when opening pages with
  mechanize.
  [deiferni]

- Also provide advice for available options in exception message.
  [lgraf]


1.19.1 (2015-08-20)
-------------------

- Preserve radio-button input when filling forms with radio buttons.
  [deiferni]


1.19.0 (2015-07-31)
-------------------

- Implement browser.click_on(tex) short cut for clicking links.
  [jone]

- Fix encoding error in assertion message when selecting a missing select
  option.
  [mbaechtold]


1.18.1 (2015-07-23)
-------------------

- Fix GET form submission to actually submit it with GET.
  [jone]


1.18.0 (2015-07-22)
-------------------

- Table: add new ".column" method for getting all cells of a column.
  [jone]


1.17.0 (2015-07-22)
-------------------

- Add support for filling ``collective.z3cform.datagridfield``.
  [jone, mbaechtold]


1.16.1 (2015-07-13)
-------------------

- Autocomplete widget: extract URL from javascript.
  [jone]


1.16.0 (2015-07-08)
-------------------

- Add image upload widget support (archetypes and dexterity).
  [jone]


1.15.0 (2015-05-07)
-------------------

- Parse XML responses with XML parser instead of HTML parser.
  New methods for parsing the response: ``parse_as_html``,
  ``parse_as_xml`` and ``parse``.
  [jone]

- Add browser properties ``contenttype``, ``mimetype`` and ``encoding``.
  [jone]


1.14.6 (2015-04-17)
-------------------

- Use ``cssselect`` in favor of ``lxml.cssselect``.
  This allows us to use ``lxml >= 3``.
  [jone]

- Added tests for z3c date fields.
  [phgross]


1.14.5 (2015-01-30)
-------------------

- AutocompleteWidget: Drop query string from base URL when building query URL.
  [lgraf]


1.14.4 (2014-10-03)
-------------------

- Widgets: test for sequence widget after testing for autocomplete widgets.
  Some widgets match both, autocomplete and sequence widgets.
  In this case we want to have the autocomplete widget.
  [jone]


1.14.3 (2014-10-02)
-------------------

- Fix error with textarea tags without id-attributes.
  [jone]


1.14.2 (2014-09-29)
-------------------

- Fix an issue with relative urls.
  [jone, deiferni]


1.14.1 (2014-09-26)
-------------------

- Set the HTTP ``REFERER`` header correctly.
  [jone]


1.14.0 (2014-09-26)
-------------------


- Add folder_contents page object.
  [jone]

- Update table methods with keyword arguments:

  - head_offset: used for stripping rows from the header
  - as_text: set to False for getting cell nodes

  [jone]


1.13.4 (2014-09-22)
-------------------

- Filling selects: verbose error message when option not found.
  The available options are now included in the message.
  [jone]


1.13.3 (2014-09-02)
-------------------

- Node.text: remove multiple spaces in a row caused by nesting.
  [jone]


1.13.2 (2014-08-06)
-------------------

- Fix problems when filling forms which have checked checkedbox.
  [phgross]


1.13.1 (2014-07-15)
-------------------

- Fix encoding problem on binary file uploads.
  [jone]


1.13.0 (2014-06-12)
-------------------

- Add a Dexterity namedfile upload widget.
  [lgraf]


1.12.4 (2014-05-30)
-------------------

- Fix python 2.6 support.
  [jone]


1.12.3 (2014-05-30)
-------------------

- Fix z3cform choice collection widget to support Plone < 4.3.
  [jone]


1.12.2 (2014-05-29)
-------------------

- Fix z3cform choice collection widget submit value.
  The widget creates hidden input fields on submit.
  [jone]


1.12.1 (2014-05-29)
-------------------

- Fix error in z3cform choice collection widget when using paths.
  [jone]


1.12.0 (2014-05-29)
-------------------

- Add a z3cform choice collection widget.
  This is used for z3cform List fields with Choice value_type.
  [jone]

- Add select field node wrapper with methods for getting available options.
  [jone]


1.11.4 (2014-05-22)
-------------------

- browser.open(data): support multiple values for the same data name.
  The values can either be passed as a dict with lists as values or as
  a sequence of two-element tuples.
  [jone]


1.11.3 (2014-05-19)
-------------------

- Fix browser.url regression when the previous request raised an exception.
  [jone]


1.11.2 (2014-05-17)
-------------------

- Make NoElementFound exception message more verbose.
  When a `.first` on an empty result set raises a NoElementFound
  exception, the exception message now includes the original query.
  [jone]


1.11.1 (2014-05-17)
-------------------

- Fix browser cloning regression in autocomplete widget "query".
  The cloned browser did no longer have the same headers / cookies,
  causing authenticated access to be no longer possible.
  [jone]

- New browser.clone method for creating browser clones.
  [jone]

- Update standard page objects to accept browser instace as keyword arguments.
  This makes it possible to use the page objects with non-standard browsers.
  [jone]


1.11.0 (2014-05-14)
-------------------

- New browser.base_url property, respecting the <base> tag.
  [jone]

- New browser.debug method, opening the current page in your real browser.
  [jone]

- New browser.on method, a lazy variant of browser.open.
  [jone]

- New browser.reload method, reloading the current page.
  [jone]

- Improve requests library support:

  - Support choosing requests library, make Zope app setup optional.
    When no Zope app is set up, the ``requests`` library is set as default,
    otherwise ``mechanize``.
  - Support form submitting with requests library.
  - Improve login and header support for equests library requests.
  - Add browser.cookies support for requests library requests.
  - Use requests library sessions, so that cookies and headers persist.
  - Automatically use "POST" when data is submitted.

  [jone]

- Login improvements:

  - Support passing member objects to browser.login().
    The users / members are still expected to hav TEST_USER_PASSWORD as password.

  - Refactor login to use the new request header methods.

  [jone]

- Add request header methods for managing permanent request headers:

  - browser.append_request_header
  - browser.replace_request_header
  - browser.clear_request_header

  [jone]

- Refactor Form: eliminate class methods and do not use the global browser.
  This improves form support when running multiple browser instances concurrently.

  - Form.field_labels (class method) is now a instance property and public API.
  - Form.find_widget_in_form (class method) is removed and replaced with
    Form.find_widget (instance method).
  - Form.find_field_in_form (class method) is removed and replaced
    Form.get_field (instance method).
  - Form.find_form_element_by_label_or_name (class method) is removed and replaced
    with browser.find_form_by_field.
  - Form.find_form_by_labels_or_names (class method) is removed and replaced with
    browser.find_form_by_fields.
  - New Form.action_url property with the full qualified action URL.
  - Fix form action URL bug when using relative paths in combination with
    document-style base url.

  [jone]

- Fix wrapping input.label - this did only work for a part of field types.
  [jone]

- Fix UnicodeDecodeError in node string representation.
  [mathias.leimgruber]


1.10.0 (2014-03-19)
-------------------

- Add NodeWrapper-properties:

  - innerHTML
  - normalized_innerHTML
  - outerHTML
  - normalized_outerHTML

  [jone, elioschmutz]


1.9.0 (2014-03-18)
------------------

- Add support for filling AT MultiSelectionWidget.
  [jone]


1.8.0 (2014-03-04)
------------------

- Add a ``context`` property to the browser with the current
  context (Plone object) of the currently viewed page.
  [jone]


1.7.3 (2014-02-28)
------------------

- Fix encoding problem in factories menu page object.
  The problem occured when having a "Restrictions..." entry in the menu.
  [jone]


1.7.2 (2014-02-25)
------------------

- Form: Support checking checkboxes without a value.
  Checkboxes without a value attribute are invalid but common.
  The default browser behavior is to fallback to the value "on".
  [jone]


1.7.0 (2014-02-03)
------------------

- ContentTreeWidget: support filling objects as values.
  [jone]


1.6.1 (2014-01-31)
------------------

- Implement `logout` on browser, logout before each login.
  [jone]


1.6.0 (2014-01-29)
------------------

- Add `cookies` property to the browser.
  [jone]


1.5.3 (2014-01-28)
------------------

- Fix multiple wrapping on browser.forms.
  [jone]


1.5.2 (2014-01-17)
------------------

- Implement archetypes datetime widget form filling.
  [jone]


1.5.1 (2014-01-07)
------------------

- Fix encoding problems when posting unicode data directly with Browser.open.
  [jone]

- Support form filling with bytestrings.
  [jone]

- Fix form filling with umlauts.
  [jone]

- Fix form fill for single select fields.
  [jone]


1.5.0 (2014-01-03)
------------------

- Implement AT file upload widget, because the label does not work.
  [jone]

- Implement file uploads.
  [jone]

- Add "headers" property on the browser.
  [jone]


1.4.0 (2013-12-27)
------------------

- Deprecate `normalized_text` method, replace it with `text` property.
  The `text` property is more intuitive and easier to remember.
  The `text` property has almost the same result as `normalized_text`,
  but it represents `<br/>` and `<p>` with single and double newlines respectively.
  `text` is to be the lxml `text` property, which contained the raw, non-recursive
  text of the current node and is now available as `raw_text` property.
  [jone]

- open_html: make debugging file contain passed HTML.
  [jone]

- Sequence widget: implement custom form filling with label support and validation.
  [jone]

- Sequence widget: add additional properties with inputs and options.
  [jone]


1.3.0 (2013-12-11)
------------------

- Implement "query" method on autocomplete widget.
  [jone]

- Implement form fill for z3cform datetime widget.
  [jone]

- Fix setting attributes on nodes when wrapped with NodeWrapper.
  [jone]

- Implement form fill for z3cform autocomplete widgets.
  [jone]

- Implement form fill for z3cform sequence widgets.
  [jone]

- Add ``webdav`` method for doing WebDAV requests with a ZServer.
  [jone]


1.2.0 (2013-11-24)
------------------

- Add `open_html` method to browser object, allowing to pass in HTML directly.
  [jone]


1.1.0 (2013-11-07)
------------------

- Add dexterity page object, refactor z3cform page object.
  [jone]

- Add table nodes with helpers for table testing.
  [jone]

- Merging "Nodes" lists returns a new "Nodes" list, not a "list".
  [jone]

- Show containing elements in string representation of "Nodes" list.
  [jone]

- Fix direct child selection with CSS (node.css(">tag")).
  [jone]

- Add a ``recursive`` option to ``normalized_text``.
  [jone]


1.0.2 (2013-10-31)
------------------

- When normalizing whitespaces, do also replace non-breaking spaces.
  [jone]


1.0.1 (2013-10-31)
------------------

- Add ``first_or_none`` property to ``Nodes``.
  [jone]


1.0.0 (2013-10-28)
------------------

- Initial implementation.
  [jone]
