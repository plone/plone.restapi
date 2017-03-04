# convenience makefile to boostrap & run buildout

virtualenv = virtualenv-2.7

all: .installed.cfg
	bin/test

.installed.cfg: bin/buildout buildout.cfg *.cfg
	bin/buildout

define cfg
[buildout]
extends = plone-4.3.x.cfg
endef
export cfg

buildout.cfg:
	test -e $@ || echo "$$cfg" > $@

bin/buildout: bin/pip requirements.txt buildout.cfg
	bin/pip install --upgrade pip setuptools zc.buildout
	@touch -c $@

bin/python bin/pip:
	$(virtualenv) --clear .

clean:
	git clean -Xdf

.PHONY: all clean
