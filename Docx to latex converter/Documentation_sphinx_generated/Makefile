# Makefile for Sphinx documentation

# You can set these variables to customize the build
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = DocToLatex
SOURCEDIR     = source
BUILDDIR      = build

# Targets for building documentation
.PHONY: help clean html latexpdf

help:
	@$(SPHINXBUILD) -M help $(SOURCEDIR) $(BUILDDIR)

clean:
	@rm -rf $(BUILDDIR)/*

html:
	@$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

latexpdf:
	@$(SPHINXBUILD) -b latex $(SOURCEDIR) $(BUILDDIR)/latex
	@cd $(BUILDDIR)/latex && make all-pdf
