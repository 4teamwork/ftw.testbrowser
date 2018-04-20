from ftw.testbrowser.utils import is_installed
from operator import attrgetter
import pkg_resources


def get_plone_extras_dependencies():
    """Return a list of package names of the ftw.testbrowser[plone] extras.
    """
    dist = pkg_resources.get_distribution('ftw.testbrowser')
    primary_dependencies = set(map(attrgetter('project_name'), dist.requires()))
    primary_and_plone_dependencies = set(map(attrgetter('project_name'), dist.requires(['plone'])))
    return list(sorted(primary_and_plone_dependencies - primary_dependencies))


HAS_PLONE_EXTRAS = is_installed(*get_plone_extras_dependencies())
