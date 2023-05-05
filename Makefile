
# This Makefile assumes it's being run someplace with pip available
include reqs/Makefile.piptools
-include Makefile.proj

PROJ=$(shell python setup.py --name)

.PHONY: default
default::
	@echo "dev - set up the dev virtualenv"
	@echo "wheel|$(PROJ) - build the $(PROJ) python package"
	@echo "update-deps - rebuild package requirements"
	@echo "reinstall-deps - reinstall packages from requirements"
	@echo "pylint - run a linter on the codebase"
	@echo "mypy - run a typechecker on the codebase"
	@echo "test = run all tests in dev machine python"
	@echo "clean - remove all build artifacts"
	@echo "veryclean - remove all build artifacts and nuke test containers"
	@echo "git-release - tag a release and push it to github"
	@echo "pypi-release - push the latest release to pypi"


PYTEST_ARGS = --timeout=10 $(PYTEST_EXTRA)

PIP_VENDORED_DIR=vendor/wheel
PREREQS=setuptools
DEVREQS=reqs/dev-requirements.txt
REQS=reqs/requirements.txt
DEV_ENV=.pip_syncd

ifdef PIP_VENDORED_DIR
PIP_VENDORED_FLAGS += -f $(PIP_VENDORED_DIR)
endif

PYTEST=$(VIRTUAL_ENV)/bin/pytest

# Note that piptools refuses to put setuptools in a requirements file.

$(DEV_ENV): $(PIP_COMPILE)
	@git config --add core.hooksPath .git-hooks
	pip install --upgrade $(PREREQS)
	pip-sync $(PIP_VENDORED_FLAGS) $(DEVREQS) $(REQS)
	touch $(DEV_ENV)

$(PYTEST): $(DEV_ENV)

.PHONY: dev
dev: $(DEV_ENV)

.PHONY: nuke-stamp
nuke-stamp:
	-rm -f $(DEV_ENV)

.PHONY: reinstall-deps
reinstall-deps: nuke-stamp dev

# beware unobvious recursion: this target is called by Dockerfile
# ...which is used by the 'docker build' in the docker target
wheel:
	python setup.py bdist_wheel

raw-mypy raw-pylint raw-test raw-coverage: export PYTHONWARNINGS=ignore,default:::$(PROJ)

CODECOV_OUTPUT=--cov-report term


pylint: $(DEV_ENV)
	pylint --rcfile=.pylintrc --errors-only $(PROJ)
#	pytest $(PROJ) \
#		--pylint --pylint-rcfile=.pylintrc \
#		--pylint-error-types=EF \
#		--ignore=.direnv \
#		-m pylint

pytest-clean:
	pytest --cache-clear

.coverage:
	@echo "You must run tests first!"
	exit 1

coverage-html.zip: .coverage
	coverage html -d htmlconv
	cd htmlconv && zip -r ../$@ .

coverage.xml: .coverage
	coverage xml

test: $(DEV_ENV)
	pytest tests $(PYTEST_ARGS) -l

testf: PYTEST_EXTRA=--log-cli-level=DEBUG -lx --ff
testf: test

.PHONY: mypy
mypy:
	pytest --mypy -m mypy $(PROJ)

.PHONY: coverage
coverage:
	pytest --cov=$(PROJ) $(CODECOV_OUTPUT) tests $(PYTEST_ARGS)

.PHONY: veryclean
veryclean: clean
	-if [ -f .version ]; then \
		docker rmi -f $(PROJ):pre-`cat .version` ;\
		docker rmi -f $(PROJ):pre-`cat .version`-build ;\
		docker rmi -f $(PROJ):pre-`cat .version`-test ;\
		docker rmi -f $(PROJ):`cat .version`-build ;\
	fi


.PHONY: not-dirty
not-dirty:
	@if [ `git status --short | wc -l` != 0 ]; then\
	        echo "Uncommited code. Aborting." ;\
	        exit 1;\
	fi

#SIGN=--sign
SIGN=

.PHONY: git-release-check
git-release-check: .version
	@if [ `git rev-parse --abbrev-ref HEAD` != main ]; then \
		echo "You can only do a release from the main branch.";\
		exit 1;\
	fi
	@if git tag | grep -q `cat .version` ; then \
	        echo "Already released this version.";\
	        echo "Update the version number and try again.";\
	        exit 1;\
	fi

.PHONY: git-release
git-release: wheel .version git-release-check not-dirty pylint
	VER=`cat .version` &&\
	git push &&\
	git tag $(SIGN) $$VER &&\
	git push --tags &&\
	git checkout release &&\
	git merge main --ff-only &&\
	git push && git checkout main
	@echo "Released! Note you're now on the 'main' branch."
	
.PHONY: git-release-done-check
git-release-done-check: .version
	@VER=`cat .version` &&\
	if [ `git rev-parse HEAD` != `git rev-parse $$VER` ]; then \
		echo "You can only do a release from the main branch when it's the latest version.";\
		exit 1;\
	fi

.PHONY: pypi-releasea
pypi-release: .version git-release-done-check
	rm dist/*
	VER=`cat .version` &&\
	git checkout HEAD
	python setup.py bdist_wheel
	twine upload dist/*


# contort a bit to get the version number
.version: setup.py
	python setup.py --version >$@

.PHONY: clean
clean:
	rm -rf build dist *.egg-info shippable .version *.whl $(DEV_ENV)
	find . -name __pycache__ | xargs rm -rf
	find . -name \*.pyc | xargs rm -f

