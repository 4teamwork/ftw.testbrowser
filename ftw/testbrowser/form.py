from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
import lxml.html.formfill


class Form(NodeWrapper):

    def __init__(self, node):
        self.node = node

    @property
    def values(self):
        return self.node.fields

    @wrapped_nodes
    def find_field(self, label_or_name):
        return self.__class__.find_field_in_form(self.node, label_or_name)

    @wrapped_nodes
    def find_button_by_label(self, label):
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
        """
        values = self.field_labels_to_names(values)

        # lxml.html.formfill breaks textarea when filling.
        # see https://github.com/lxml/lxml/pull/127/files
        for fieldname, value in values.items():
            field = self.__class__.find_field_in_form(self.node, fieldname)
            if field and field.tag == 'textarea':
                field.node.text = value
                del values[fieldname]

        lxml.html.formfill._fill_form(self.node, values)
        return self

    def submit(self, button=None):
        """Submits the form.
        """

        extra_values = None
        if button and button.attrib.get('name', None) and \
                button.attrib.get('value', None):
            extra_values = {button.attrib['name']: button.attrib['value']}

        return lxml.html.submit_form(self.node,
                                     extra_values=extra_values,
                                     open_http=self._submit_form)

    def field_labels_to_names(self, values):
        """Accepts a dict and converts its field labels (keys) to field names.
        """
        new_values = {}
        for label_or_name, value in values.items():
            name = self.field_label_to_name(label_or_name)
            new_values[name] = value
        return new_values

    def field_label_to_name(self, label):
        """Accepts a field label (or a field name) and returns the field name
        of the field.
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
        for form in klass.get_browser().root.forms:
            if klass.find_field_in_form(form, label_or_name) is not None:
                return form
        return None

    @classmethod
    @wrapped_nodes
    def find_field_in_form(klass, form, label_or_name):
        label = normalize_spaces(label_or_name)

        for input in form.inputs:
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
                label = input.label is not None and normalize_spaces(input.label.text)
                if label:
                    labels.append(label)
                elif input.name:
                    labels.append(input.name)

        return labels

    def _submit_form(self, method, URL, values):
        self.__class__.get_browser().open(URL, data=values)


class SubmitButton(NodeWrapper):

    def click(self):
        return self.form.submit(button=self)

    @property
    @wrapped_nodes
    def form(self):
        for node in self.iterancestors():
            if node.tag == 'form':
                return node
        return None
