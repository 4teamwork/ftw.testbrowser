from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
import lxml.html.formfill


class Form(object):

    def __init__(self, form_node):
        self.form_node = form_node

    @property
    def values(self):
        return self.form_node.fields

    def find_field(self, label_or_name):
        return self.__class__.find_field_in_form(self.form_node, label_or_name)

    def find_button_by_label(self, label):
        for input in self.form_node.inputs:
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
        lxml.html.formfill._fill_form(self.form_node, values)
        return self

    def submit(self):
        """Submits the form.
        """
        return lxml.html.submit_form(self.form_node,
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
        field = self.__class__.find_field_in_form(self.form_node, label)
        if field is None:
            raise FormFieldNotFound(label)
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
                raise FormFieldNotFound(label_or_name)
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
    def find_field_in_form(klass, form, label_or_name):
        for input in form.inputs:
            if input.name == label_or_name:
                return input

            if input.label is None:
                continue

            if input.label.text_content() == label_or_name:
                return input

        return None

    def _submit_form(self, method, URL, values):
        self.__class__.get_browser().open(URL, data=values)
