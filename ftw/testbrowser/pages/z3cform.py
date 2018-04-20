from ftw.testbrowser import browser as default_browser


def erroneous_fields(form, browser=default_browser):
    """Returns a mapping of erroneous fields (key is label or name of
    the field) to a list of error messages for the fields on the form
    passed as argument.

    :param form: The form node to check for errors.
    :type form: :py:class:`ftw.testbrowser.form.Form`
    :param browser: A browser instance. (Default: global browser)
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: A dict of erroneous fields with error messages.
    :rtype: dict
    """

    result = {}
    for field in form.css('.field.error'):
        errors = field.css('.fieldErrorBox').text
        result[field.css('label, div.label').first.text] = errors

    return result
