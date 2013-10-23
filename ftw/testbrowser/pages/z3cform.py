from ftw.testbrowser import browser
from ftw.testbrowser.utils import normalize_spaces


def erroneous_fields():
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
