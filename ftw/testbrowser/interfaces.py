from zope.interface import Interface


class IBrowser(Interface):

    def open(url_or_object, data=None, view=None):
        """Open the browser and go to an URL or visit the default view of
        an object.

        ``url_or_object`` - an URL (string or unicode) or an object which has
        an ``absolute_url`` returning an URL.

        ``data`` - a dict with form data, where the key is the name of the
        field and the value is the value of the field.

        ``view`` - a view name (string or unicode), which is appended to the
        URL. This is especially useful combined with passing in objects.
        """
