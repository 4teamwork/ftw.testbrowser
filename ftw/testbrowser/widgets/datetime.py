from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class DateTimeWidget(PloneWidget):
    """Represents the z3cform datetime widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        name = PloneWidget(node).fieldname
        if not name:
            return False

        return len(node.css('input[name="%s-day"]' % name)) > 0

    def fill(self, value):
        """Fill the widget fields with a datetime object.

        :param value: datetime object for filling the fields.
        :type value: :py:class:`datetime.datetime`
        """
        name = self.fieldname

        self.css('*[name="%s-day"]' % name).first.set('value', str(value.day))
        self.css('*[name="%s-month"]' % name).first.value = str(value.month)
        self.css('*[name="%s-year"]' % name).first.set(
            'value', str(value.year))

        if self.css('*[name="%s-hour"]' % name):
            self.css('*[name="%s-hour"]' % name).first.set(
                'value', str(value.hour))
            self.css('*[name="%s-min"]' % name).first.set(
                'value', str(value.minute))
