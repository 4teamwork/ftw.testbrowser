from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import Interface


page_source = CatalogSource(portal_type='Document')


class IDXTypeSchema(Interface):

    relation_choice = RelationChoice(
        title=u'Relation-Choice',
        source=page_source,
        required=True,
    )

    relation_list = RelationList(
        title=u'Relation-List',
        default=[],
        value_type=RelationChoice(
            title=u"Relation-List",
            source=page_source,
            ),
        required=True,
        )
