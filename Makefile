### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
PYTHON?=python3

# installed?
ifeq (, $(shell which $(PYTHON) ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif

# version ok?
PYTHON_VERSION_MIN=3.10
PYTHON_VERSION_OK=$(shell $(PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_VERSION_MIN)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Need python $(PYTHON_VERSION) >= $(PYTHON_VERSION_MIN)")
endif

BACKEND_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

GIT_FOLDER=$(BACKEND_FOLDER)/.git
VENV_FOLDER=$(BACKEND_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin

# Sphinx variables
# You can set these variables from the command line.
SPHINXOPTS      ?=
# Internal variables.
SPHINXBUILD     = "$(realpath bin/sphinx-build)"
SPHINXAUTOBUILD = "$(realpath bin/sphinx-autobuild)"
DOCS_DIR        = ./docs/source/
BUILDDIR        = ../_build/
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS) .

all: help

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '##'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## Clean environment
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	git clean -Xdf

.PHONY: clean-instance
clean-instance: ## remove existing instance
	rm -fr instance etc inituser var

.PHONY: clean-venv
clean-venv: ## remove virtual environment
	rm -fr $(BIN_FOLDER) env pyvenv.cfg .tox .pytest_cache requirements-mxdev.txt

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

$(BIN_FOLDER)/pip $(BIN_FOLDER)/tox $(BIN_FOLDER)/mxdev: ## Set up Python virtual environment
	@echo "$(GREEN)==> Setup Python virtual environment$(RESET)"
	$(PYTHON) -m venv $(VENV_FOLDER)
	$(BIN_FOLDER)/pip install -U "pip" "pipx" "wheel" "cookiecutter" "mxdev" "tox" "pre-commit" -c constraints.txt
	$(BIN_FOLDER)/pre-commit install

instance/etc/zope.ini: $(BIN_FOLDER)/pipx  ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	$(BIN_FOLDER)/pipx run cookiecutter -f --no-input --config-file instance.yaml gh:plone/cookiecutter-zope-instance

$(BIN_FOLDER)/runwsgi $(BIN_FOLDER)/zope-testrunner: ## Install Plone
	@echo "$(GREEN)==> Install Plone$(RESET)"
	$(BIN_FOLDER)/mxdev -c mx.ini
	$(BIN_FOLDER)/pip install -r requirements-mxdev.txt

.PHONY: start
start: $(BIN_FOLDER)/runwsgi instance/etc/zope.ini  ## Start a Zope instance on localhost:8080
	$(BIN_FOLDER)/runwsgi instance/etc/zope.ini

## Dev tools

.PHONY: check
check: $(BIN_FOLDER)/tox ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	$(BIN_FOLDER)/tox -e lint

.PHONY: test
test: $(BIN_FOLDER)/zope-testrunner ## Run tests
	$(BIN_FOLDER)/zope-testrunner --all --test-path=src -s plone.restapi

## Performance tests (need to be updated)

# .PHONY: Test Performance
# test-performance:
# 	jmeter -n -t performance.jmx -l jmeter.jtl

# .PHONY: Test Performance Locust Querystring Search
# test-performance-locust-querystring-search:
# 	bin/locust -f performance/querystring-search.py --host http://localhost:12345/Plone --users 100 --spawn-rate 5 --run-time 5m --autostart

# .PHONY: Test Performance Locust Querystring Search CI
# test-performance-locust-querystring-search-ci:
# 	bin/locust -f performance/querystring-search.py --host http://localhost:12345/Plone --users 100 --spawn-rate 5 --run-time 5m --headless --csv=example

## Documentation

.PHONY: docs-clean
docs-clean:  ## Clean current and legacy docs build directories
	cd $(DOCS_DIR) && rm -rf $(BUILDDIR)/
	rm -rf docs/build

$(BIN_FOLDER)/sphinx-autobuild $(BIN_FOLDER)/sphinx-build: $(BIN_FOLDER)/pip  ## Install dependencies for building docs
	$(BIN_FOLDER)/pip install -r requirements-docs.txt

.PHONY: docs-livehtml
docs-livehtml: $(BIN_FOLDER)/sphinx-autobuild  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	cd "$(DOCS_DIR)" && $(BIN_FOLDER)/sphinx-autobuild \
		--ignore "*.swp" \
		-b html . "$(BUILDDIR)/html" $(SPHINXOPTS)

.PHONY: docs-linkcheckbroken
docs-linkcheckbroken: $(BIN_FOLDER)/sphinx-build  ## Run linkcheck and show only broken links
	cd $(DOCS_DIR) && $(BIN_FOLDER)/sphinx-build -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=auto  && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: rtd-pr-preview
rtd-pr-preview: $(BIN_FOLDER)/sphinx-build  ## Build pull request preview on Read the Docs
	cd $(DOCS_DIR) && $(BIN_FOLDER)/sphinx-build -b html $(ALLSPHINXOPTS) ${READTHEDOCS_OUTPUT}/html/
