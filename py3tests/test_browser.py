from ftw.testbrowser import browser
from unittest import TestCase


class TestRequest(TestCase):

    def test(self):
        with browser:
            browser.open('https://google.ch')
            browser.fill({'q': 'testbrowser'}).submit()
