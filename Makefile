.PHONY: help Makefile
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

prev_line_help = None
for line in sys.stdin:
	if prev_line_help is None:
		match = re.match(r"^## (.*)", line)
		if match:
			prev_line_help = match.groups()[0]
		else:
			prev_line_help = None
	else:
		match = re.match(r'^([a-zA-Z_-]+)', line)
		if match:
			target = match.groups()[0]
			print("%-22s %s" % (target, prev_line_help))

		target = None
		prev_line_help = None

endef
export PRINT_HELP_PYSCRIPT

define CHECKOUT_STABLE
	cd plotnine && \
	VERSION=$$(git tag | grep -E '^[v]?[0-9]+\.[0-9]+\.[0-9]+$$' | sort -V | tail -n 1) && \
	git checkout "$$VERSION"
endef
export CHECKOUT_STABLE


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

## Remove Quarto website build files
clean:
	rm -rf _site
	rm -rf _extensions
	rm -rf images
	rm -rf reference
	rm -f _variables.yml
	rm -f changelog.qmd
	rm -f qrenderer.scss
	rm -f plotnine.scss
	rm -f objects.txt
	rm -f objects.inv
	cd plotnine/doc && make clean

## Update git submodules to commits referenced in this repository
submodules:
	git submodule init
	git submodule update --depth=20

## Pull latest commits in git submodules
submodules-pull:
	git submodule update --recursive --remote

submodules-tags:
	git submodule foreach --recursive 'git fetch --tags'


checkout-pr: submodules submodules-pull submodules-tags

## Checkout stable (released) version
checkout-stable: submodules submodules-pull submodules-tags
	 $(CHECKOUT_STABLE)

## Checkout the latest on the main branch
checkout-latest: submodules submodules-pull submodules-tags
	cd plotnine && git checkout main

## Checkout the dev branch
checkout-dev: submodules submodules-pull submodules-tags
	cd plotnine && git fetch --depth=1 origin dev && git checkout -b dev

## Install build dependencies
deps:
	cd plotnine/doc && make deps

## Setup notebooks from plotnine-examples
plotnine-examples:
	python _plotnine_examples.py

## Build plotnine API qmd pages
api-pages: plotnine-examples
	cd plotnine/doc && make docstrings

## Copy API artefacts into website
copy-api-artefacts: api-pages
	# Copy all relevant files
	rsync -av plotnine/doc/_extensions .
	rsync -av plotnine/doc/images .
	rsync -av plotnine/doc/reference .
	rsync -av plotnine/doc/_variables.yml .
	rsync -av plotnine/doc/changelog.qmd .
	rsync -av plotnine/doc/qrenderer.scss .
	rsync -av plotnine/doc/plotnine.scss .
	rsync -av plotnine/doc/objects.txt .
	rsync -av plotnine/doc/objects.inv .

## Download interlinks
interlinks:
	quartodoc interlinks

## Build all pages for the website
pages: copy-api-artefacts
	# Create gallery and tutorials pages
	python gallery/_create.py
	python tutorials/_create.py

## Build website
site: pages
	quarto render

## Build website in a new environment
site-cold: deps interlinks site

## Build website and serve
preview:
	quarto preview
