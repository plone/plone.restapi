# convenience makefile to boostrap & run buildout

virtualenv = virtualenv-2.7

all: .installed.cfg
	bin/test

.installed.cfg: bin/buildout *.cfg
	bin/buildout

bin/buildout: bin/pip
	bin/pip install --upgrade pip setuptools zc.buildout
	@touch -c $@

bin/python bin/pip:
	$(virtualenv) --clear .

clean:
	git clean -Xdf

.PHONY: all clean
