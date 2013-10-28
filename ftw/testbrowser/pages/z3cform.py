from ftw.testbrowser import browser
from ftw.testbrowser.utils import normalize_spaces


def erroneous_fields():
    """Returns a mapping of erroneous fields (key is label or name of
    the field) to a list of error messages for this field.
    """

    result = {}
    for input in browser.css('form#form').first.inputs:
        if not input.parent('.field.error'):
            continue

        if input.label is not None:
            label = input.label.text_content()
        if not label:
            label = input.name

        errors = input.parent('.field').css('.fieldErrorBox').normalized_text()
        result[normalize_spaces(label)] = errors
    return result
