from plone.z3cform.layout import FormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface
import json


class IShoppingFormSchema(Interface):

    fruits = schema.List(
        title=u'Fruits',
        value_type=schema.Choice([u'Apple', u'Banana', u'Orange']),
        required=False)

    bag = schema.List(
        title=u'Bag',
        value_type=schema.Choice([u'plastic bag', u'paper bag']),
        required=False)


class ShoppingForm(Form):
    label = u'Shopping'
    ignoreContext = True
    fields = Fields(IShoppingFormSchema)

    def __init__(self, *args, **kwargs):
        super(ShoppingForm, self).__init__(*args, **kwargs)
        self.result_data = None

    def update(self):
        self.fields['fruits'].widgetFactory = CheckBoxFieldWidget
        self.fields['bag'].widgetFactory = RadioFieldWidget
        return super(ShoppingForm, self).update()

    @buttonAndHandler(u'Submit')
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) == 0:
            self.result_data = dict([(key, value) for (key, value) in data.items()
                                     if value])


class ShoppingView(FormWrapper):

    form = ShoppingForm

    def render(self):
        if self.form_instance.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.form_instance.result_data)
        else:
            return super(ShoppingView, self).render()
