from ftw.testbrowser import browser
from ftw.testbrowser.utils import normalize_spaces


def messages():
    """Returns a dict with lists of status messages (normalized text) for
    "info", "warning" and "error".
    """

    messages = {'info': [],
                'warning': [],
                'error': []}

    for message in browser.css('.portalMessage'):
        type_classes = (set(message.classes) & set(messages.keys()))
        if not type_classes:
            # unkown message type - skip it
            continue

        key = tuple(type_classes)[0]
        text = normalize_spaces(' '.join(message.css('dd').text_content()))
        if not text:
            # message is empty - skip it
            continue

        messages[key].append(text)

    return messages


def info_messages():
    """Returns all "info" statusmessages.
    """
    return messages()['info']


def warning_messages():
    """Returns all "warning" statusmessages.
    """
    return messages()['warning']


def error_messages():
    """Returns all "error" statusmessages.
    """
    return messages()['error']


def as_string(filter_=None):
    """All status messages as string instead of dict, so that it can be used
    for formatting assertion errors.
    Pass a type ("info", "warning" or "error") for filter_ing the messages.
    """

    if filter_ is None:
        filter_ = ('info', 'warning', 'error')
    elif isinstance(filter_, (str, unicode)):
        filter_ = (filter_,)

    result = []
    for msg_type, msg_texts in sorted(messages().items()):
        if msg_type not in filter_:
            continue

        for text in msg_texts:
            result.append('"[%s] %s"' % (msg_type.upper(), text))
    return ', '.join(result)


def assert_message(text):
    """Assert that a status message is visible.
    """
    all_messages = reduce(list.__add__, messages().values())
    if text not in all_messages:
        raise AssertionError('No status message "%s". Current messages: %s' % (
                text, as_string()))
    return True


def assert_no_messages():
    """Assert that there are no status messages at all.
    """
    all_messages = reduce(list.__add__, messages().values())
    if len(all_messages) > 0:
        raise AssertionError('Unexpected status messages: %s' % as_string())
    return True


def assert_no_error_messages():
    """Assert that there are no error messages.
    """
    if len(error_messages()) > 0:
        raise AssertionError('Unexpected "error" status messages: %s' % (
                as_string('error')))
    return True
