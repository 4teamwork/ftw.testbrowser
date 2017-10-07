from ftw.testbrowser import exceptions
from ftw.testbrowser.queryinfo import QueryInfo
from unittest2 import TestCase


class Foo(object):
    def __repr__(self):
        return u'<Foo>'

    @QueryInfo.build
    def method(self, one=None, two=None, three=None, four=None, query_info=None):
        return query_info

    @classmethod
    @QueryInfo.build
    def classmethod(klass, one=None, two=None, query_info=None):
        return query_info

    @QueryInfo.build
    def arbitrary_args(self, one=None, *args, **kwargs):
        return kwargs['query_info']

    @QueryInfo.build
    def nesting(self, one=None, **kwargs):
        return self.method(one=one, **kwargs)


@QueryInfo.build
def bar(one=None, two=None, three=None, query_info=None):
    return query_info


@QueryInfo.build
def show_hint(name=None, query_info=None):
    query_info.add_hint('Valid names: Franzisika, Fritz')
    return query_info


class TestQueryInfo(TestCase):

    def test_instance_method(self):
        self.assertEquals(
            '<Foo>.method()',
            Foo().method().render_call())

    def test_instance_method_with_positional_arguments(self):
        self.assertEquals(
            "<Foo>.method(1, 'two')",
            Foo().method(1, 'two').render_call())

    def test_instance_method_with_keyword_arguments(self):
        # The order is always the order of the function definition.
        # We do not know in which order the keyword arguments are
        # ordered on call time.
        self.assertEquals(
            "<Foo>.method(one=1, two='two')",
            Foo().method(two='two', one=1).render_call())

    def test_instance_method_with_mixed_arguments(self):
        self.assertEquals(
            "<Foo>.method(1, 'two', four=[0, 1, 2, 3])",
            Foo().method(1, 'two', four=range(4)).render_call())

    def test_arbitrary_args(self):
        self.assertEquals(
            "<Foo>.arbitrary_args(1, 2, foo='Foo')",
            Foo().arbitrary_args(1, 2, foo='Foo').render_call())

    def test_class_method(self):
        self.assertEquals(
            "Foo.classmethod(1, two='two')",
            Foo.classmethod(1, two='two').render_call())

    def test_nesting_method_keeps_first_queryinfo(self):
        self.assertEquals(
            "<Foo>.nesting(one=1, two='two')",
            Foo().nesting(one=1, two='two').render_call())

    def test_module_function_with_arguments(self):
        self.assertEquals(
            "test_queryinfo.bar(1, three='three')",
            bar(1, three='three').render_call())

    def test_render_with_hint(self):
        self.assertEquals(
            "test_queryinfo.show_hint('Hans')\n"
            'Valid names: Franzisika, Fritz',
            show_hint('Hans').render())
