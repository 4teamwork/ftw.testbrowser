import pkg_resources


try:
    pkg_resources.get_distribution('Zope')
except pkg_resources.DistributionNotFound:
    HAS_ZOPE4 = False
else:
    HAS_ZOPE4 = True
