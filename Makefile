.PHONY: help Makefile plotnine-examples
.DEFAULT_GOAL := help

SOURCE_DIR=source
SITE_DIR=$(SOURCE_DIR)/_site
PYTHON ?= python

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

define CHECKOUT_RELEASE
	cd plotnine && \
	VERSION=$$(git tag | grep -E '^[v]?[0-9]+\.[0-9]+\.[0-9]+$$' | sort -V | tail -n 1) && \
	git checkout "$$VERSION"
endef
export CHECKOUT_RELEASE

define CHECKOUT_PRE_RELEASE
	cd plotnine && \
	VERSION=$$(git tag | grep -E '^[v]?[0-9]+\.[0-9]+\.[0-9]+a[0-9]+$$' | sort -V | tail -n 1) && \
	git checkout "$$VERSION"
endef
export CHECKOUT_PRE_RELEASE

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

## Remove Quarto website build files
clean:
	rm -rf $(SITE_DIR)/
	rm -rf $(SOURCE_DIR)/_extensions
	rm -rf $(SOURCE_DIR)/images
	rm -rf $(SOURCE_DIR)/reference
	rm -f  $(SOURCE_DIR)/_variables.yml
	rm -f  $(SOURCE_DIR)/changelog.qmd
	rm -f  $(SOURCE_DIR)/qrenderer.scss
	rm -f  $(SOURCE_DIR)/plotnine.scss
	rm -f  $(SOURCE_DIR)/objects.txt
	rm -f  $(SOURCE_DIR)/objects.inv
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

## Checkout released version
checkout-release: submodules submodules-pull submodules-tags
	 $(CHECKOUT_RELEASE)

## Checkout released version
checkout-pre-release: submodules submodules-pull submodules-tags
	 $(CHECKOUT_PRE_RELEASE)

## Checkout the latest on the main branch
checkout-main: submodules submodules-pull submodules-tags
	cd plotnine && git checkout main

## Checkout the dev branch
checkout-dev: submodules submodules-pull submodules-tags
	cd plotnine && git fetch --depth=1 origin dev && git checkout -b dev

## Install build dependencies
install:
	uv sync

## Install all dependencies required for development (requires nodejs & npm)
install-full: install
	uv pip install jinja2-cli
	npm ci

## Setup notebooks from plotnine-examples
plotnine-examples:
	$(PYTHON) ./scripts/get_plotnine_examples.py

## Generate home page items
homepage:
	uv run scripts/generate-homepage-items.sh

## Build plotnine API qmd pages
api-pages: plotnine-examples
	cd plotnine/doc && make docstrings

## Copy API artefacts into website
copy-api-artefacts: api-pages # copy-guide
	# Copy all relevant files
	rsync -av plotnine/doc/_extensions $(SOURCE_DIR)
	rsync -av plotnine/doc/images $(SOURCE_DIR)
	rsync -av plotnine/doc/reference $(SOURCE_DIR)
	rsync -av plotnine/doc/_variables.yml $(SOURCE_DIR)
	rsync -av plotnine/doc/changelog.qmd $(SOURCE_DIR)
	rsync -av plotnine/doc/qrenderer.scss $(SOURCE_DIR)
	rsync -av plotnine/doc/plotnine.scss $(SOURCE_DIR)
	rsync -av plotnine/doc/objects.txt $(SOURCE_DIR)
	rsync -av plotnine/doc/objects.inv $(SOURCE_DIR)
	# Correct
	$(PYTHON) ./scripts/patch_api_artefacts.py

copy-guide: 
	rm -rf plotnine-guide $(SOURCE_DIR)/guide
	git clone -n -b refactor-guide-contained --depth=1 --filter=tree:0 https://github.com/machow/plotnine-guide.git
	cd plotnine-guide \
	  && git sparse-checkout set --no-cone /guide \
	  && git checkout
	mv plotnine-guide/guide $(SOURCE_DIR)/guide
	rm -rf plotnine-guide

## Download interlinks
interlinks:
	cd $(SOURCE_DIR) && uv run quartodoc interlinks

## Build all pages for the website
pages: copy-api-artefacts
	# Create gallery and tutorials pages
	$(PYTHON) ./scripts/create_gallery.py
	$(PYTHON) ./scripts/create_tutorials.py

## Build website
site: pages
	cd $(SOURCE_DIR) && uv run quarto render
	$(PYTHON) ./scripts/postprocess_site.py $(SOURCE_DIR)/_quarto.yml
	touch $(SITE_DIR)/.nojekyll

## Build website in a new environment
site-cold: install interlinks site

## Build website and serve
preview:
	cd $(SOURCE_DIR) && quarto preview
