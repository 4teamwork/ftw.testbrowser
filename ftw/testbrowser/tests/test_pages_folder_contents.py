from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import folder_contents
from ftw.testbrowser.table import TableRow
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestFolderContents(FunctionalTestCase):

    def setUp(self):
        super(TestFolderContents, self).setUp()
        self.grant('Manager')

    @browsing
    def test_titles(self, browser):
        create(Builder('page').titled(u'An exotic page'))
        browser.login().open(view='folder_contents')
        self.assertEquals(['An exotic page'], folder_contents.titles())

    @browsing
    def test_select__selects_from_objects(self, browser):
        foo = create(Builder('page').titled(u'Foo'))
        bar = create(Builder('page').titled(u'Bar'))

        browser.login().open(view='folder_contents')
        folder_contents.select(foo, bar)
        self.assertEquals(
            ('/plone/foo', '/plone/bar'),
            folder_contents.selected_paths())

    @browsing
    def test_select_by_title(self, browser):
        create(Builder('page').titled(u'Foo'))
        create(Builder('page').titled(u'Bar'))

        browser.login().open(view='folder_contents')
        folder_contents.select_by_title('Foo', 'Bar')
        self.assertEquals(
            ('/plone/foo', '/plone/bar'),
            folder_contents.selected_paths())

    @browsing
    def test_select_by_path(self, browser):
        foo = create(Builder('page').titled(u'Foo'))
        foo_path = '/'.join(foo.getPhysicalPath())
        bar = create(Builder('page').titled(u'Bar'))
        bar_path = '/'.join(bar.getPhysicalPath())

        browser.login().open(view='folder_contents')
        folder_contents.select_by_path(foo_path, bar_path)
        self.assertEquals(
            ('/plone/foo', '/plone/bar'),
            folder_contents.selected_paths())

    @browsing
    def test_row_by_title(self, browser):
        create(Builder('page').titled(u'Foo'))
        browser.login().open(view='folder_contents')

        with self.assertRaises(ValueError) as cm:
            folder_contents.row_by_title('Bar')
        self.assertEquals('No row with title "Bar" found.',
                          str(cm.exception))

        self.assertEquals(TableRow, type(folder_contents.row_by_title('Foo')))

        create(Builder('page').titled(u'Foo'))
        browser.reload()
        with self.assertRaises(ValueError) as cm:
            folder_contents.row_by_title('Foo')
        self.assertEquals(
            'More than one row with title "Foo" found: ' +
            "['{0}/foo', '{0}/foo-1']".format(self.portal.portal_url()),
            str(cm.exception))

    @browsing
    def test_row_by_object(self, browser):
        obj = create(Builder('folder').titled(u'Foo'))
        subobj = create(Builder('page').titled(u'Bar').within(obj))
        browser.login().open(view='folder_contents')

        self.assertEquals(TableRow, type(folder_contents.row_by_object(obj)))

        with self.assertRaises(ValueError) as cm:
            folder_contents.row_by_object(subobj)
        self.assertEquals(
            'The object with path "/plone/foo/bar" is not visible.'
            " Visible objects: ['/plone/foo']",
            str(cm.exception))

    @browsing
    def test_row_by_path(self, browser):
        obj = create(Builder('folder').titled(u'Foo'))
        subobj = create(Builder('page').titled(u'Bar').within(obj))
        browser.login().open(view='folder_contents')

        obj_path = '/'.join(obj.getPhysicalPath())
        subobj_path = '/'.join(subobj.getPhysicalPath())

        self.assertEquals(TableRow,
                          type(folder_contents.row_by_path(obj_path)))

        with self.assertRaises(ValueError) as cm:
            folder_contents.row_by_path(subobj_path)
        self.assertEquals(
            'The object with path "/plone/foo/bar" is not visible.'
            " Visible objects: ['/plone/foo']",
            str(cm.exception))
