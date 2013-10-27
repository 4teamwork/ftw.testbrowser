# Makefile for Sphinx documentation
#

SPHINXBUILD   = ./bin/sphinx-build
BUILDDIR      = docs

.PHONY: help html

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"

html:
	$(SPHINXBUILD) -b html ${BUILDDIR}/source $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."
