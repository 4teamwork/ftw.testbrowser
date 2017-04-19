from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
import json


@widget
class DateTimeWidget(PloneWidget):
    """Represents the z3cform datetime widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        name = PloneWidget(node, node.browser).fieldname
        if not name:
            return False

        return bool(DateTimeWidget(node, node.browser)._field('day'))

    def fill(self, value):
        """Fill the widget fields with a datetime object.

        :param value: datetime object for filling the fields.
        :type value: :py:class:`datetime.datetime`
        """

        self._field('day').value = value.strftime('%-d')
        self._field('month').value = value.strftime('%-m')
        self._field('year').value = value.strftime('%Y')

        if not self._field('hour'):
            return

        if self._field('ampm'):
            self._field('hour').value = value.strftime('%I')
            self._field('ampm').value = value.strftime('%p')

        else:
            self._field('hour').value = value.strftime('%H')

        minute = self._field('min') or self._field('minute')
        minute.value = value.strftime('%M')

    def _field(self, component):
        xpr = '*[name="%(name)s-%(cmp)s"], *[name="%(name)s_%(cmp)s"]' % {
            'name': self.fieldname,
            'cmp': component}
        if len(self.css(xpr)) == 0:
            return None
        else:
            return self.css(xpr).first


@widget
class PaternslibDateTimeWidget(PloneWidget):
    """Represents the z3cform paternslib datetime widget.
    """

    field_selector = '>input[data-pat-pickadate]'

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css(PaternslibDateTimeWidget.field_selector)) == 1

    def fill(self, value):
        field = self.css(PaternslibDateTimeWidget.field_selector).first
        config = json.loads(field.attrib['data-pat-pickadate'])

        if config.get('time'):
            field.set('value', value.strftime('%Y-%m-%d %H:%M'))
        else:
            field.set('value', value.strftime('%Y-%m-%d'))
