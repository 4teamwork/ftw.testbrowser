from plone.testing import Layer


class DefaultDriverFixture(Layer):

    def __init__(self, library_constant):
        super(DefaultDriverFixture, self).__init__(
            name='DefaultDriverFixture:{}'.format(library_constant))
        self.library_constant = library_constant

    def setUp(self):
        from ftw.testbrowser import browser
        self.previous_default_driver = browser.default_driver
        browser.default_driver = self.library_constant

    def tearDown(self):
        from ftw.testbrowser import browser
        browser.default_driver = self.previous_default_driver
