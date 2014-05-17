from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.pages import z3cform


def erroneous_fields(browser=default_browser):
    """Returns a mapping of erroneous fields (key is label or name of
    the field) to a list of error messages for the fields on a dexterity
    add and edit forms (`form#form`).

    :returns: A dict of erroneous fields with error messages.
    :rtype: dict
    """
    form = browser.css('form#form').first
    return z3cform.erroneous_fields(form)
