# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for documentation
html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# Multi-language documentation
html-multilang:
	@echo "Building English documentation..."
	@$(SPHINXBUILD) -b html -D language=en "$(SOURCEDIR)" "$(BUILDDIR)/html/en" $(SPHINXOPTS) $(O)
	@echo "Building Russian documentation..."
	@$(SPHINXBUILD) -b html -D language=ru "$(SOURCEDIR)" "$(BUILDDIR)/html/ru" $(SPHINXOPTS) $(O)
	@echo "Building Azerbaijani documentation..."
	@$(SPHINXBUILD) -b html -D language=az "$(SOURCEDIR)" "$(BUILDDIR)/html/az" $(SPHINXOPTS) $(O)
	@echo "Building main documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Multi-language build finished. The HTML pages are in $(BUILDDIR)/html."

linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)
	@echo "Link check finished. Check $(BUILDDIR)/linkcheck/output.txt for any issues."

clean:
	rm -rf $(BUILDDIR)/*
