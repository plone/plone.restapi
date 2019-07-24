# keep in sync with: https://github.com/kitconcept/buildout/edit/master/Makefile
# update by running 'make update'
SHELL := /bin/bash
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

version = 2.7

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

all: .installed.cfg

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: Update Makefile and Buildout
update: ## Update Make and Buildout
	wget -O Makefile https://raw.githubusercontent.com/kitconcept/buildout/master/Makefile
	wget -O requirements.txt https://raw.githubusercontent.com/kitconcept/buildout/master/requirements.txt
	wget -O plone-4.3.x.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/plone-4.3.x.cfg
	wget -O plone-5.1.x.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/plone-5.1.x.cfg
	wget -O plone-5.2.x.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/plone-5.2.x.cfg
	wget -O travis.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/travis.cfg
	wget -O versions.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/versions.cfg

.installed.cfg: bin/buildout *.cfg
	bin/buildout

bin/buildout: bin/pip
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	@touch -c $@

.PHONY: Build Plone 4.3
build-plone-4.3: .installed.cfg ## Build Plone 4.3
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/buildout -c plone-4.3.x.cfg

.PHONY: Build Plone 5.0
build-plone-5.0: .installed.cfg ## Build Plone 5.0
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/buildout -c plone-5.0.x.cfg

.PHONY: Build Plone 5.1
build-plone-5.1: .installed.cfg  ## Build Plone 5.1
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/buildout -c plone-5.1.x.cfg

.PHONY: Build Plone 5.2
build-plone-5.2: .installed.cfg  ## Build Plone 5.2
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/buildout -c plone-5.2.x.cfg

 ## Build Plone 5.2 with Python 3
build-py3:  ## Build Plone 5.2 with Python 3
	virtualenv --python=python3 .
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/pip install black
	bin/buildout -c plone-5.2.x.cfg

bin/python bin/pip:
	virtualenv --clear --python=python$(version) .

.PHONY: Test
test:  ## Test
	bin/test

.PHONY: Test Performance
test-performance:
	jmeter -n -t performance.jmx -l jmeter.jtl

.PHONY: Code Analysis
code-analysis:  ## Code Analysis
	bin/code-analysis

.PHONY: Build Docs
docs:  ## Build Docs
	bin/sphinxbuilder

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
