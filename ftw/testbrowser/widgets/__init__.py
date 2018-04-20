from ftw.testbrowser.compat import HAS_PLONE_EXTRAS

if HAS_PLONE_EXTRAS:
    from ftw.testbrowser.widgets import datetime
    from ftw.testbrowser.widgets import file
    from ftw.testbrowser.widgets import sequence
    from ftw.testbrowser.widgets import autocomplete
    from ftw.testbrowser.widgets import atmultiselect
    from ftw.testbrowser.widgets import z3cchoicecollection
    from ftw.testbrowser.widgets import datagridwidget
