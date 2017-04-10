from collections import defaultdict
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
from ftw.testbrowser.widgets.base import PloneWidget
from mechanize._form import MimeWriter
from StringIO import StringIO
import lxml.html.formfill
import mimetypes
import shutil
import urllib
import urlparse


class Form(NodeWrapper):

    @property
    def values(self):
        """Returns the lxml `FieldsDict` of this form.

        :returns: lxml fields dict
        :rtype: lxml.html.FieldsDict
        """
        return self.node.fields

    @property
    @wrapped_nodes
    def inputs(self):
        """Returns a list of all input nodes of this form.

        :returns: All input nodes
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        inputs = list(self.node.inputs)

        for button in self.browser.document.xpath("//button"):
            inputs.append(button)
        return inputs

    @wrapped_nodes
    def find_field(self, label_or_name):
        """Finds and returns a field by label or name.

        :param label_or_name: The label or the name of the field.
        :type label_or_name: string
        :returns: The field node
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """
        label = normalize_spaces(label_or_name)

        for input in self.inputs:
            if input.name == label_or_name:
                return input

            if input.label is None:
                continue

            if label in (input.label.text,
                         normalize_spaces(input.label.raw_text)):
                return input

        return self.find_widget(label_or_name)

    @wrapped_nodes
    def find_submit_buttons(self):
        """Returns all submit buttons of this form.

        :returns: a list of submit buttons
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
          of :py:class:`ftw.testbrowser.form.SubmitButton` of
        """
        for field in self.inputs:
            if not isinstance(field, SubmitButton):
                continue
            if field.form != self:
                continue
            yield field

    @wrapped_nodes
    def find_button_by_label(self, label):
        """Finds a button of with a specific label in this form.

        :param label: The label of the button.
        :type label: string
        :returns: The button node
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        for input in self.inputs:
            try:
                input_type = input.type
            except AttributeError:
                continue

            if input_type not in ('submit', 'reset', 'button'):
                continue

            if input.value == label or input.text == label:
                return input

    def fill(self, values):
        """Accepts a dict, where the key is the name or the label of a field
        and the value is its new value and fills the form with theese values.

        :param values: The key is the label or input-name and the value is the
          value to set.
        :type values: dict
        :returns: The form node.
        :rtype: :py:class:`ftw.testbrowser.form.Form`
        """
        values = self.field_labels_to_names(values)
        to_unicode = (lambda val: isinstance(val, str) and
                      val.decode('utf-8') or val)
        values = dict(map(lambda item: map(to_unicode, item), values.items()))

        widgets = []

        for fieldname, value in values.items():
            field = self.find_field(fieldname)
            if isinstance(field, PloneWidget):
                widgets.append((field, value))
                continue

            # lxml.html.formfill breaks textarea when filling.
            # see https://github.com/lxml/lxml/pull/127/files
            if field and field.tag == 'textarea':
                field.node.text = value
                del values[fieldname]

            # lxml.html.formfill cannot fill select fields properly.
            if field and field.tag == 'select' and not field.get('multiple'):
                field.value = value
                del values[fieldname]

            # lxml.html.formfill cannot handle file uploads.
            # We use mechanize to do this.
            if field and field.tag == 'input' and field.type == 'file':
                field.set('value', value)
                del values[fieldname]

            # lxml.html.formfill expects the checkbox value to be the value
            # of the field, otherwise it will not be checked.
            # We like to be able to use `True` for checking the checkbox
            # independent of the actual field value.
            if field and field.tag == 'input' and field.type == 'checkbox' \
                    and value is True:
                values[fieldname] = field.node.attrib.get('value', 'on')

        values = self._merge_already_checked_inputs(values)

        lxml.html.formfill._fill_form(self.node, values)

        for widget, value in widgets:
            widget.fill(value)

        return self

    def _merge_already_checked_inputs(self, values):
        # Given a form with an already checked input element (e.g.
        # checked=checked), when this form is filled without changing the input
        # element the lxml formfill unchecks the element.
        # Therefore we need to re-add all already checked inputs to
        # the values to fill unless the value is meant to be changed.
        to_merge = defaultdict(list)

        for input in self.inputs:
            if input.name in values:
                continue

            input_type = input.attrib.get('type', '').lower()
            if input_type not in ['checkbox', 'radio']:
                continue

            if input.attrib.get('checked', None) is not None:
                to_merge[input.name].append(input.attrib.get('value', 'on'))

        values.update(to_merge)
        return values

    def submit(self, button=None):
        """Submits this form by clicking on the first submit button.
        The behavior of click the first submit button is what browser usually
        do and may not get the expected results.

        It might be more save to click the primary button specificall:

        .. code:: py

          browser.find('Save').click()
          # or
          form.save()

        .. seealso:: :py:func:`save`
        """

        if button is None:
            # Simulate the behavior as browser such as Chrome do: when pressing
            # enter (similar with form.submit()) the value of the first submit
            # button is sent as if it was clicked.
            buttons = self.find_submit_buttons()
            if len(buttons) > 0:
                return buttons.first.click()

        extra_values = None
        if button and button.attrib.get('name', None):
            extra_values = {
                button.attrib['name']: button.attrib.get('value', '')}
        return lxml.html.submit_form(self.node,
                                     extra_values=extra_values,
                                     open_http=self._submit_form)

    def save(self):
        """Clicks on the "Save" button in this form.
        """
        return self.find('Save').click()

    def field_labels_to_names(self, values):
        """Accepts a dict and converts its field labels (keys) to field names.

        :param values: A dict of values where the keys are field labels.
        :type values: dict
        :param values: A dict of values where the keys are field names.
        :rtype: dict
        """
        new_values = {}
        for label_or_name, value in values.items():
            name = self.field_label_to_name(label_or_name)
            if name is None:
                name = label_or_name
            new_values[name] = value
        return new_values

    def field_label_to_name(self, label):
        """Accepts a field label (or a field name) and returns the field name
        of the field.

        :param label: The label of the field.
        :type label: string
        :returns: The field name of the field.
        :rtype: string
        """
        field = self.find_field(label)
        if field is None:
            raise FormFieldNotFound(label, self.field_labels)
        return getattr(field, 'name', None)

    @property
    def field_labels(self):
        """A list of label texts and field names of each field in this form.

        The list contains the whitespace normalized label text of
        each field.
        If there is no label or it has an empty text, the fieldname
        is used instead.

        :returns: A list of label texts (and field names).
        :rtype: list of strings
        """
        labels = []
        for input in self.inputs:
            label = (input.label is not None and
                     normalize_spaces(input.label.text))
            if label:
                labels.append(label)
            elif input.name:
                labels.append(input.name)

        return labels

    def find_widget(self, label):
        """Finds a Plone widget (div.field) in a form.

        :param label: The label of the widget.
        :type label: string
        :returns: Returns the field node or `None`.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        label = normalize_spaces(label)

        label_node_xpath = '//label[normalize-space(text())="%s"]' % label
        div_node_xpath = '//div[contains(concat(" ",' + \
            'normalize-space(@class)," ")," label ")]' + \
            '[normalize-space(text())="%s"]' % label
        label_xpath = ' | '.join((label_node_xpath, div_node_xpath))

        for label_node in self.xpath(label_xpath):
            if not label_node.within(self):
                continue

            field = label_node.parent(css='div.field')
            if field:
                return field

        return None

    @property
    def action_url(self):
        """The full qualified URL to send the form to.
        This should imitate normal browser behavior:

        If the action is full qualified, use it as it is.
        If the action is relative, make it absolute by joining
        it with the page's base URL.
        If there is no action, the action is the current page URL.

        The page's base URL can be set in the HTML document with
        a ``<base>``-tag, otherwise the page URL is used.
        """

        action = self.attrib.get('action', None)
        if not action:
            return self.browser.url

        if urlparse.urlparse(action).scheme:
            # The action is full qualified
            return action

        return urlparse.urljoin(self.browser.base_url, action)

    def _submit_form(self, method, URL, values):
        URL = self.action_url

        if method.lower() == 'get':
            if '?' in URL:
                URL += '&' + urllib.urlencode(values)
            else:
                URL += '?' + urllib.urlencode(values)
            return self.browser.open(URL, referer=True)

        request_body, request_headers = self._prepare_multipart_request(
            URL, values)
        return self.browser.open(URL,
                                 data=request_body,
                                 headers=dict(request_headers),
                                 method='POST',
                                 referer=True)

    def _prepare_multipart_request(self, URL, values):
        data = StringIO()
        http_headers = []
        mw = MimeWriter(data, http_headers)
        mw.startmultipartbody("form-data", add_to_http_hdrs=True, prefix=0)

        for fieldname, value in values:
            field = self.find_field(fieldname)
            if isinstance(field, FileField):
                field.write_mime_data(mw)
            else:
                mw2 = mw.nextpart()
                mw2.addheader("Content-Disposition",
                              'form-data; name="%s"' % fieldname, 1)
                f = mw2.startbody(prefix=0)
                f.write(value)

        mw.lastpart()
        value = data.getvalue()
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value, http_headers


class TextAreaField(NodeWrapper):
    """The `TextAreaField` node wrapper wraps a text area field and makes sure
    that the TinyMCE widget finds its label, since the markup of the TinyMCE
    widget is not standard.
    """

    def __init__(self, node, browser):
        super(TextAreaField, self).__init__(node, browser)
        self._setup_label()

    def _setup_label(self):
        if self.node.label is not None:
            return

        if not self.attrib.get('id', None):
            return

        # Tinymce with dexterity has not the same label "for" as ids
        # on the textarea.
        for_attribute = self.attrib['id'].replace('.', '-')
        label = self.body.xpath('//label[@for="%s"]' % for_attribute)
        if len(label) > 0:
            self.node.label = label.first.node


class SubmitButton(NodeWrapper):
    """Wraps a submit button and makes it clickable.
    """

    def click(self):
        """Click on this submit button, which makes the form submit with this
        button.
        """
        return self.form.submit(button=self)

    @property
    @wrapped_nodes
    def form(self):
        """Returns the form of which this button is parent.
        It returns the first form node if it is a nested form.

        :returns: the form node
        :rtype: :py:class:`ftw.testbrowser.form.Form`
        """
        for node in self.iterancestors():
            if node.tag == 'form':
                return node
        return None


class FileField(NodeWrapper):
    """The ``FileField`` wrapper wraps `<input type="file" />` fields.
    Since lxml.html.formfill cannot handle file uploads it does this with
    mechanize, which takes care of multipart requests.
    """

    def set(self, attrname, value):
        if attrname != 'value':
            return self.node.set(attrname, value)

        # store the value into the browser cache, since the lxml document
        # can only store strings.
        self.browser.form_files[self.node] = self._normalize_value(value)
        self.node.set('value', '____marker____')

    def write_mime_data(self, mime_writer):
        value = self.browser.form_files.get(self.node, None)
        if value is None:
            file_object = StringIO()
            filename = ''
            content_type = 'application/octet-stream'
        else:
            file_object, filename, content_type = value

        mime_part = mime_writer.nextpart()
        mime_part.addheader(
            'Content-Disposition',
            'form-data; name="{0}"; filename="{1}"'.format(
                self.name, filename),
            prefix=1)

        filehandle = mime_part.startbody(content_type, prefix=0)
        file_object.seek(0)
        shutil.copyfileobj(file_object, filehandle)

    def _normalize_value(self, value):
        filename = None
        content_type = None

        if isinstance(value, (list, tuple)):
            if len(value) == 2:
                value, filename = value
            elif len(value) == 3:
                value, filename, content_type = value

        if not filename:
            filename = getattr(value, 'filename', getattr(value, 'name', None))

        if not filename:
            raise ValueError('Cannot upload files without a filename.')

        if not content_type:
            content_type = getattr(value, 'content_type', None)

        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] \
                or 'application/octet-stream'

        if isinstance(value, str):
            value = StringIO(value)

        return value, filename, content_type


class SelectField(NodeWrapper):
    """The ``SelectField`` wrapper wraps and extends ``<select>`` fields.
    """

    @property
    def options(self):
        """Returns a list of value/label pairs of all available options
        of this select field.

        :returns: list of tuples, each a value/label per of an option
        :rtype: list of tuples
        """
        return [(option.attrib.get('value', option.text), option.text)
                for option in self.css('>option')]

    @property
    def options_labels(self):
        """Returns a list of labels of available options.

        :returns: list of labels
        :rtype: list of strings
        """
        return [label for (value, label) in self.options]

    @property
    def options_values(self):
        """Returns a list of values of available options.

        :returns: list of values
        :rtype: list of strings
        """
        return [value for (value, label) in self.options]

    def __setattr__(self, name, value):
        if name == 'value':
            return self.set_value(value)
        return super(SelectField, self).__setattr__(name, value)

    def set_value(self, value):
        try:
            self.node.value = value
        except ValueError:
            try:
                self.node.value = dict(map(reversed, self.options))[value]
            except (KeyError, ValueError):
                options = u', '.join([u'"{1}" ({0})'.format(*option)
                                      for option in self.options])

                raise ValueError(
                    u'No option {0} for select "{1}". '
                    u'Available options: {2}.'.format(
                        repr(value), self.name, options))
