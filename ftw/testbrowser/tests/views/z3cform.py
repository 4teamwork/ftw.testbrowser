from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from datetime import date
from datetime import datetime
from plone.formwidget.autocomplete.widget import AutocompleteMultiFieldWidget
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from plone.formwidget.contenttree import UUIDSourceBinder
from plone.i18n.normalizer import idnormalizer
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.formwidget.query.interfaces import IQuerySource
from z3c.relationfield import RelationChoice
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import json


class PaymentVocabulary(SimpleVocabulary):
    implements(IVocabularyFactory, IQuerySource)

    def __init__(self):
        super(PaymentVocabulary, self).__init__([
                SimpleTerm(u'cash', u'cash', u'Cash'),
                SimpleTerm(u'mastercard', u'mastercard', u'MasterCard'),
                SimpleTerm(u'visa', u'visa', u'Visa')])

    def search(self, query_string):
        query_string = query_string.lower()
        for term in self():
            if query_string in term.title.lower():
                yield term

    def __call__(self, context=None):
        return self


def make_term_from_title(title):
    token = idnormalizer.normalize(title)
    return SimpleTerm(token, token, title)


class ICakeSchema(Interface):
    quantity = schema.Int(
        title=u'Quantity',
        required=True,
    )

    cake = schema.Choice(
        title=u'Cake',
        required=True,
        vocabulary=SimpleVocabulary(
            map(make_term_from_title,
                [u'Hot Milk Cake',
                 u'Chocolate Truffle Cake',
                 u'Cream Cheese Pound Cake',
                 u'Toffee Poke Cake',
                 u'Ultimate Chocolate Cheese Cake'])
        )
    )

    low_fat = schema.Bool(
        title=u'Low-fat',
        required=False,
    )

    reference = RelationChoice(
        title=u'Reference',
        source=UUIDSourceBinder(),
        required=False,
    )


class IShoppingFormSchema(Interface):

    fruits = schema.List(
        title=u'Fruits',
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary(
                [SimpleTerm(u'apple', u'apple', u'Apple'),
                 SimpleTerm(u'banana', u'banana', u'Banana'),
                 SimpleTerm(u'orange', u'orange', u'Orange')])),
        required=False)

    bag = schema.List(
        title=u'Bag',
        value_type=schema.Choice([u'plastic bag', u'paper bag']),
        required=False)

    payment = schema.List(
        title=u'Payment',
        value_type=schema.Choice(
            vocabulary='test-z3cform-payment-vocabulary'),
        required=False)

    delivery_date = schema.Datetime(
        title=u'Delivery date',
        required=False)

    day_of_payment = schema.Date(
        title=u'Day of payment',
        required=False)

    documents = schema.List(
        title=u'Documents',
        value_type=schema.Choice(
            source=PathSourceBinder(portal_type='Document')))

    cakes = schema.List(
        title=u'Cakes',
        value_type=DictRow(title=u'Cake', schema=ICakeSchema),
        required=False,
        missing_value=[],
    )


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
        self.fields['payment'].widgetFactory = AutocompleteMultiFieldWidget
        self.fields['documents'].widgetFactory = MultiContentTreeFieldWidget
        self.fields['cakes'].widgetFactory = DataGridFieldFactory
        return super(ShoppingForm, self).update()

    def updateWidgets(self, prefix=None):
        super(ShoppingForm, self).updateWidgets(prefix)
        self.widgets['cakes'].allow_reorder = False

    @buttonAndHandler(u'Submit')
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.result_data = {}
        for key, value in data.items():
            if not value:
                continue

            if isinstance(value, (datetime, date)):
                value = value.isoformat()

            self.result_data[key] = value


class ShoppingView(FormWrapper):

    form = ShoppingForm

    def render(self):
        if self.form_instance.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.form_instance.result_data)
        else:
            return super(ShoppingView, self).render()
