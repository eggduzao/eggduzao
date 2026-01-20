PY?=
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

# new: content dirs
POSTDIR=$(INPUTDIR)/blog
PAGEDIR=$(INPUTDIR)/pages
DATE=$(shell date +%Y-%m-%d)

GITHUB_PAGES_BRANCH=main
GITHUB_PAGES_COMMIT_MESSAGE=Generate Pelican site

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

SERVER ?= "0.0.0.0"

PORT ?= 0
ifneq ($(PORT), 0)
	PELICANOPTS += -p $(PORT)
endif

help:
	@echo 'Makefile for a pelican Web site                                           '
	@echo '                                                                          '
	@echo 'Usage:                                                                    '
	@echo '   make html                           (re)generate the web site          '
	@echo '   make clean                          remove the generated files         '
	@echo '   make regenerate                     regenerate files upon modification '
	@echo '   make publish                        generate using production settings '
	@echo '   make serve [PORT=8000]              serve site at http://localhost:8000'
	@echo '   make serve-global [SERVER=0.0.0.0]  serve (as root) to $(SERVER):80    '
	@echo '   make devserver [PORT=8000]          serve and regenerate together      '
	@echo '   make devserver-global               regenerate and serve on 0.0.0.0    '
	@echo '   make github                         upload the web site via gh-pages   '
	@echo '   make newpost title="My Title"       create a new blog post             '
	@echo '   make newpage title="About"          create a new static page           '
	@echo '                                                                          '
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html   '
	@echo 'Set the RELATIVE variable to 1 to enable relative urls                    '
	@echo '                                                                          '

html:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

clean:
	[ ! -d "$(OUTPUTDIR)" ] || rm -rf "$(OUTPUTDIR)"

regenerate:
	"$(PELICAN)" -r "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve:
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve-global:
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b $(SERVER)

devserver:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

devserver-global:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b 0.0.0.0

publish:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)

github: publish
	ghp-import -m "$(GITHUB_PAGES_COMMIT_MESSAGE)" -b $(GITHUB_PAGES_BRANCH) "$(OUTPUTDIR)" --no-jekyll
	git push origin $(GITHUB_PAGES_BRANCH)

newpost:
	@if [ -z "$(title)" ]; then \
		echo "Usage: make newpost title=\"My post title\""; \
		exit 1; \
	fi
	@mkdir -p "$(POSTDIR)"
	@slug=$$(echo "$(title)" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'); \
	filename="$(POSTDIR)/$(DATE)-$$slug.md"; \
	echo "Creating $$filename"; \
	{ \
		echo "Title: $(title)"; \
		echo "Date: $(DATE) 12:00"; \
		echo "Category: blog"; \
		echo "Tags: "; \
		echo "Slug: $$slug"; \
		echo "Authors: Eduardo G. Gusmão"; \
		echo "Summary: "; \
		echo ""; \
		echo "Write your post here."; \
	} > $$filename

newpage:
	@if [ -z "$(title)" ]; then \
		echo "Usage: make newpage title=\"About\""; \
		exit 1; \
	fi
	@mkdir -p "$(PAGEDIR)"
	@slug=$$(echo "$(title)" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'); \
	filename="$(PAGEDIR)/$$slug.md"; \
	echo "Creating $$filename"; \
	{ \
		echo "Title: $(title)"; \
		echo "Save_as: $$slug.html"; \
		echo "URL: $$slug.html"; \
		echo ""; \
		echo "Write your page here."; \
	} > $$filename

.PHONY: html help clean regenerate serve serve-global devserver devserver-global publish github newpost newpage
