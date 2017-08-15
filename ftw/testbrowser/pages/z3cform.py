from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.utils import normalize_spaces


def erroneous_fields(form=None):
    """Returns a mapping of erroneous fields (key is label or name of
    the field) to a list of error messages for the fields on the form
    passed as argument.

    :param form: The form node to check for errors. Defaults to the form with
      the id `#form` in the default browser.
    :type form: :py:class:`ftw.testbrowser.form.Form`
    :returns: A dict of erroneous fields with error messages.
    :rtype: dict
    """
    if form is None:
        form = default_browser.forms.get('form')
        if form is None:
            available_forms = default_browser.forms.keys()
            raise ValueError(
                'Could not find the default `#form` on the current page, '
                'please provide a valid form. Available forms are: {0}'
                .format(available_forms))

    result = {}
    for input in form.inputs:
        if not input.parent('.field.error'):
            continue

        if input.label is not None:
            label = input.label.text_content()
        if not label:
            label = input.name

        errors = input.parent('.field').css('.fieldErrorBox').normalized_text()
        result[normalize_spaces(label)] = errors
    return result
