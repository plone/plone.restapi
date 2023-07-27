SHELL := /bin/bash
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

version = 3

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Sphinx variables
# You can set these variables from the command line.
SPHINXOPTS      ?=
# Internal variables.
SPHINXBUILD     = $(realpath bin/sphinx-build)
SPHINXAUTOBUILD = $(realpath bin/sphinx-autobuild)
DOCS_DIR        = ./docs/source/
BUILDDIR        = ../_build/
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS) .
VALEFILES       := $(shell find $(DOCS_DIR) -type f -name "*.md" -print)

all: build-plone-6.0

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.installed.cfg: bin/buildout *.cfg

bin/buildout: bin/pip
	bin/pip install --upgrade pip
	bin/pip install -r requirements-5.2.txt
	bin/pip install -c constraints.txt black
	@touch -c $@

bin/python bin/pip:
	python$(version) -m venv . || virtualenv --python=python$(version) .
	bin/python -m pip install --upgrade pip
	bin/pip install -r requirements-docs.txt

.PHONY: Build Plone 5.2
build-plone-5.2: .installed.cfg  ## Build Plone 5.2
	bin/pip install --upgrade pip
	bin/pip install -r requirements-5.2.txt
	bin/buildout -c plone-5.2.x.cfg

.PHONY: Build Plone 5.2 Performance
build-plone-5.2-performance: .installed.cfg  ## Build Plone 5.2
	bin/pip install --upgrade pip
	bin/pip install -r requirements-5.2.txt
	bin/buildout -c plone-5.2.x-performance.cfg

.PHONY: Build Plone 6.0
build-plone-6.0: .installed.cfg  ## Build Plone 6.0
	bin/pip install --upgrade pip
	bin/pip install -r requirements-6.0.txt
	bin/buildout -c plone-6.0.x.cfg

.PHONY: Build Plone 6.0 Performance
build-plone-6.0-performance: .installed.cfg  ## Build Plone 6.0
	bin/pip install --upgrade pip
	bin/pip install -r requirements-6.0.txt
	bin/buildout -c plone-6.0.x-performance.cfg

.PHONY: start
start: ## Start Plone Backend
	@echo "$(GREEN)==> Start Plone Backend$(RESET)"
	PYTHONWARNINGS=ignore bin/instance fg

.PHONY: Test
test:  ## Test
	bin/test

.PHONY: Test Performance
test-performance:
	jmeter -n -t performance.jmx -l jmeter.jtl

.PHONY: Test Performance Locust Querystring Search
test-performance-locust-querystring-search:
	bin/locust -f performance/querystring-search.py --host http://localhost:12345/Plone --users 100 --spawn-rate 5 --run-time 5m --autostart

.PHONY: Test Performance Locust Querystring Search CI
test-performance-locust-querystring-search-ci:
	bin/locust -f performance/querystring-search.py --host http://localhost:12345/Plone --users 100 --spawn-rate 5 --run-time 5m --headless --csv=example

.PHONY: Black
black:  ## Black
	if [ -f "bin/black" ]; then bin/black src/ ; fi

.PHONY: zpretty
zpretty:  ## zpretty
	if [ -f "bin/zpretty" ]; then zpretty -i ./**/*.zcml; fi

.PHONY: Build Docs
docs:  ## Build Docs
	bin/sphinxbuilder

.PHONY: docs-clean
docs-clean:  ## Clean current and legacy docs build directories, and Python virtual environment
	cd $(DOCS_DIR) && rm -rf $(BUILDDIR)/
	rm -rf bin include lib
	rm -rf docs/build

.PHONY: docs-html
docs-html: bin/python  ## Build HTML
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: docs-livehtml
docs-livehtml: bin/python  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	cd "$(DOCS_DIR)" && ${SPHINXAUTOBUILD} \
		--ignore "*.swp" \
		-b html . "$(BUILDDIR)/html" $(SPHINXOPTS)

.PHONY: docs-linkcheck
docs-linkcheck: bin/python  ## Run linkcheck
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: docs-linkcheckbroken
docs-linkcheckbroken: bin/python  ## Run linkcheck and show only broken links
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=auto  && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: docs-vale
docs-vale:  ## Run Vale style, grammar, and spell checks
	vale sync
	vale --no-wrap $(VALEFILES)
	@echo
	@echo "Vale is finished; look for any errors in the above output."

.PHONY: netlify
netlify:
	pip install -r requirements-docs.txt
	cd $(DOCS_DIR) && sphinx-build -b html $(ALLSPHINXOPTS) ../$(BUILDDIR)/html

.PHONY: Test Release
test-release:  ## Run Pyroma and Check Manifest
	bin/pyroma -n 10 -d .

.PHONY: Release
release:  ## Release
	bin/fullrelease

.PHONY: Clean
clean:  ## Clean
	git clean -Xdf

.PHONY: all clean
