MAKE ?= make
PYTHONPATH := $(PYTHONPATH):$(CURDIR)/scripts:$(CURDIR)/load-dir

.PHONY: all
all: build

.PHONY: build
build:
	$(MAKE) -C src all

pyvenv:
	virtualenv $@
	$@/bin/pip $(PIP_OPTS) install -r requirements.txt

.PHONY: check
check: pyvenv
	$</bin/pip $(PIP_OPTS) install -r requirements-test.txt
	$</bin/flake8 --max-line-length=80 scripts/authenticate

.PHONY: test
test: check
	(. pyvenv/bin/activate; \
		$(MAKE) PYTHONPATH="$(PYTHONPATH)" -C $@)

.PHONY: clean
clean:
	$(MAKE) -C src clean
	rm -rf load-dir python scripts/__pycache__
	rm -rf pyvenv
