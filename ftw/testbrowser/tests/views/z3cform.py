from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from datetime import date
from datetime import datetime
from OFS.interfaces import IItem
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.i18n.normalizer import idnormalizer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import getFSVersionTuple
from six.moves import map
from six.moves import zip
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.formwidget.query.interfaces import IQuerySource
from z3c.relationfield import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


PLONE5 = getFSVersionTuple() >= (5, 0)

if PLONE5:
    from plone.app.z3cform.widget import AjaxSelectFieldWidget
    from plone.app.z3cform.widget import RelatedItemsFieldWidget
else:
    from plone.formwidget.autocomplete.widget import AutocompleteMultiFieldWidget
    from plone.formwidget.contenttree import MultiContentTreeFieldWidget
    from plone.formwidget.contenttree import PathSourceBinder
    from plone.formwidget.contenttree import UUIDSourceBinder


@implementer(IVocabularyFactory, IQuerySource)
class PaymentVocabulary(SimpleVocabulary):

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


class ICakeSchema(model.Schema):
    quantity = schema.Int(
        title=u'Quantity',
        required=True,
    )

    cake = schema.Choice(
        title=u'Cake',
        required=True,
        vocabulary=SimpleVocabulary(
            list(map(make_term_from_title,
                     [u'Hot Milk Cake',
                      u'Chocolate Truffle Cake',
                      u'Cream Cheese Pound Cake',
                      u'Toffee Poke Cake',
                      u'Ultimate Chocolate Cheese Cake']))
        )
    )

    low_fat = schema.Bool(
        title=u'Low-fat',
        required=False,
    )

    if PLONE5:
        directives.widget(reference=RelatedItemsFieldWidget)
        reference = RelationChoice(
            title=u'Reference',
            source=CatalogSource(),
            required=False,
        )
    else:
        reference = RelationChoice(
            title=u'Reference',
            source=UUIDSourceBinder(),
            required=False,
        )


class IShoppingFormSchema(model.Schema):

    directives.widget(fruits=CheckBoxFieldWidget)
    fruits = schema.List(
        title=u'Fruits',
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary(
                [SimpleTerm(u'apple', u'apple', u'Apple'),
                 SimpleTerm(u'banana', u'banana', u'Banana'),
                 SimpleTerm(u'orange', u'orange', u'Orange')])),
        required=False)

    directives.widget(bag=RadioFieldWidget)
    bag = schema.List(
        title=u'Bag',
        value_type=schema.Choice([u'plastic bag', u'paper bag']),
        required=False)

    if PLONE5:
        directives.widget(
            'payment',
            AjaxSelectFieldWidget,
            vocabulary='test-z3cform-payment-vocabulary'
        )
    else:
        directives.widget(payment=AutocompleteMultiFieldWidget)
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

    if PLONE5:
        directives.widget(documents=RelatedItemsFieldWidget)
        documents = RelationList(
            title=u'Documents',
            value_type=RelationChoice(
                source=CatalogSource(portal_type='Document'),
                ),
            required=False)
    else:
        directives.widget(documents=MultiContentTreeFieldWidget)
        documents = schema.List(
            title=u'Documents',
            value_type=schema.Choice(
                source=PathSourceBinder(portal_type='Document')))

    directives.widget(cakes=DataGridFieldFactory)
    cakes = schema.List(
        title=u'Cakes',
        value_type=DictRow(title=u'Cake', schema=ICakeSchema),
        required=False,
        missing_value=[],
    )


class ShoppingForm(AutoExtensibleForm, Form):
    label = u'Shopping'
    ignoreContext = True
    schema = IShoppingFormSchema

    def __init__(self, *args, **kwargs):
        super(ShoppingForm, self).__init__(*args, **kwargs)
        self.result_data = None

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
            self.result_data[key] = value

    def render(self):
        if self.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.make_json_serializable(
                self.result_data))
        else:
            return super(ShoppingForm, self).render()

    def make_json_serializable(self, value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if IItem.providedBy(value):
            return IUUID(value)

        if isinstance(value, (list, tuple)):
            return list(map(self.make_json_serializable, value))

        if isinstance(value, dict):
            return dict(list(zip(*list(map(self.make_json_serializable,
                                           zip(*list(value.items())))))))

        return value
