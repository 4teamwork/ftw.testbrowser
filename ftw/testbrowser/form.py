from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.nodes import wrap_node
from ftw.testbrowser.utils import normalize_spaces
import lxml.html.formfill


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
        return list(self.node.inputs)

    @wrapped_nodes
    def find_field(self, label_or_name):
        """Finds and returns a field by label or name.

        :param label_or_name: The label or the name of the field.
        :type label_or_name: string
        :returns: The field node
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """
        return self.__class__.find_field_in_form(self.node, label_or_name)

    @wrapped_nodes
    def find_submit_buttons(self):
        """Returns all submit buttons of this form.

        :returns: a list of submit buttons
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
          of :py:class:`ftw.testbrowser.form.SubmitButton` of
        """

        for field in self.node.inputs:
            if field.tag != 'input':
                continue
            if getattr(field, 'type', None) != 'submit':
                continue
            button = SubmitButton(field)
            if button.form != self:
                continue
            yield button

    @wrapped_nodes
    def find_button_by_label(self, label):
        """Finds a button of with a specific label in this form.

        :param label: The label of the button.
        :type label: string
        :returns: The button node
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        for input in self.node.inputs:
            try:
                input_type = input.type
            except AttributeError:
                continue

            if input_type not in ('submit', 'reset', 'button'):
                continue

            if input.value == label:
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

        for fieldname, value in values.items():
            field = self.__class__.find_field_in_form(self.node, fieldname)

            # lxml.html.formfill breaks textarea when filling.
            # see https://github.com/lxml/lxml/pull/127/files
            if field and field.tag == 'textarea':
                field.node.text = value
                del values[fieldname]

            # lxml.html.formfill expects the checkbox value to be the value
            # of the field, otherwise it will not be checked.
            # We like to be able to use `True` for checking the checkbox
            # independent of the actual field value.
            if field and field.tag == 'input' and field.type == 'checkbox' \
                    and value is True:
                values[fieldname] = field.node.attrib['value']

        lxml.html.formfill._fill_form(self.node, values)
        return self

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
        if button and button.attrib.get('name', None) and \
                button.attrib.get('value', None):
            extra_values = {button.attrib['name']: button.attrib['value']}

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
        field = self.__class__.find_field_in_form(self.node, label)
        if field is None:
            labels = self.__class__.field_labels(self.node)
            raise FormFieldNotFound(label, labels)
        return field.name

    @classmethod
    def get_browser(klass):
        from ftw.testbrowser import browser
        return browser

    @classmethod
    def find_form_by_labels_or_names(klass, *labels_or_names):
        """Searches for the form which has fields for the labels passed as
        arguments and returns the form node.

        :returns: The form instance which has the searched fields.
        :rtype: :py:class:`ftw.testbrowser.form.Form`
        :raises: :py:exc:`ftw.testbrowser.exceptions.FormFieldNotFound`
        :raises: :py:exc:`ftw.testbrowser.exceptions.AmbiguousFormFields`
        """

        form_element = None
        for label_or_name in labels_or_names:
            form = klass.find_form_element_by_label_or_name(label_or_name)
            if form is None:
                labels = klass.field_labels(form_element)
                raise FormFieldNotFound(label_or_name, labels)
            if form_element is not None and form != form_element:
                raise AmbiguousFormFields()
            form_element = form

        return Form(form_element)

    @classmethod
    def find_form_element_by_label_or_name(klass, label_or_name):
        """Searches the form which has a field with the label or name passed as
        argument and returns the form node.
        Returns `None` when no such field was found.

        :param label_or_name: The label or the name of the field.
        :type label_or_name: string
        :returns: The form instance which has the searched fields or `None`
        :rtype: :py:class:`ftw.testbrowser.form.Form`.
        """

        for form in klass.get_browser().root.forms:
            if klass.find_field_in_form(form, label_or_name) is not None:
                return form
        return None

    @classmethod
    @wrapped_nodes
    def find_field_in_form(klass, form, label_or_name):
        """Finds and returns a field with the passed label or name in the
        passed form.

        :param form: The form node.
        :type form: :py:class:`ftw.testbrowser.form.Form`
        :param label_or_name: The label or the name of the field.
        :type label_or_name: string
        :returns: Returns the field node or `None`.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        label = normalize_spaces(label_or_name)

        for input in form.inputs:
            input = wrap_node(input)
            if input.name == label_or_name:
                return input

            if input.label is None:
                continue

            if normalize_spaces(input.label.text) == label:
                return input

            if normalize_spaces(input.label.text_content()) == label:
                return input

        return None

    @classmethod
    def field_labels(klass, form=None):
        forms = form and [form] or klass.get_browser().root.forms

        labels = []

        for form in forms:
            for input in form.inputs:
                label = (input.label is not None
                         and normalize_spaces(input.label.text))
                if label:
                    labels.append(label)
                elif input.name:
                    labels.append(input.name)

        return labels

    def _submit_form(self, method, URL, values):
        self.__class__.get_browser().open(URL, data=values)


class TextAreaField(NodeWrapper):
    """The `TextAreaField` node wrapper wraps a text area field and makes sure
    that the TinyMCE widget finds its label, since the markup of the TinyMCE
    widget is not standard.
    """

    def __init__(self, node):
        super(TextAreaField, self).__init__(node)
        self._setup_label()

    def _setup_label(self):
        if self.node.label is not None:
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
