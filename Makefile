# convenience makefile to boostrap & run buildout

version = 2.7

all: .installed.cfg
	bin/test

.installed.cfg: bin/buildout *.cfg
	bin/buildout

bin/buildout: bin/pip
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	@touch -c $@

bin/python bin/pip:
	virtualenv --clear --python=python$(version) .

build-python3:
	virtualenv --clear --python=python3 .
	bin/pip install --upgrade pip
	bin/pip install -r requirements.txt
	bin/buildout -c plone-5.2.x.cfg

test-performance:
	jmeter -n -t performance.jmx -l jmeter.jtl

clean:
	git clean -Xdf

.PHONY: all clean
