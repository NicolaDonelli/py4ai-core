# Signifies our desired python version
# Makefile macros (or variables) are defined a little bit differently than traditional bash, keep in mind that in the Makefile there's top-level Makefile-only syntax, and everything else is bash script syntax.
PYTHON = poetry run

# .PHONY defines parts of the makefile that are not dependant on any specific file
# This is most often used to store functions
.PHONY = help

folders := py4ai/core tests
files := $(shell find . -name "*.py")
doc_files := $(shell find sphinx -name "*.*")

# Uncomment to store cache installation in the environment
# cache_dir := $(shell python -c 'import site; print(site.getsitepackages()[0])')
cache_dir := .make_cache
package_name="py4ai-core"

$(shell mkdir -p $(cache_dir))

POETRY_EXISTS := $(shell command -v poetry 2> /dev/null)

pre_deps_tag := $(cache_dir)/.pre_deps
setup_tag := $(cache_dir)/.setup_tag
env_tag := $(cache_dir)/.env_tag
install_tag := $(cache_dir)/.install_tag
docker_build_tag := $(cache_dir)/.docker_build_tag

project_name := py4ai-core
registry := ghcr.io
image_name := $(registry)/nicoladonelli/$(project_name)

# ======================
# Rules and Dependencies
# ======================

help:
	@echo "---------------HELP-----------------"
	@echo "Package Name: $(package_name)"
	@echo " "
	@echo "Type 'make' followed by one of these keywords:"
	@echo " "
	@echo "  - reqs_dev to build closed development requirements, requirements/requirements_dev.txt, from requirements/requirements_dev.in and requirements/requirements.in"
	@echo "  - reqs to build closed minimal requirements, requirements/requirements.txt, from requirements/requirements.in"
	@echo "  - setup to install minimal requirements"
	@echo "  - setup_dev to install development requirements"
	@echo "  - format to reformat files to adhere to PEP8 standards"
	@echo "  - dist to build a tar.gz distribution"
	@echo "  - install to install the package with minimal requirements"
	@echo "  - install_dev to install the package with development environment"
	@echo "  - uninstall to uninstall the package and its dependencies"
	@echo "  - tests to run unittests using pytest as configured in pyproject.toml"
	@echo "  - lint to perform linting using flake8 as configured in pyproject.toml"
	@echo "  - mypy to perform static type checking using mypy as configured in pyproject.toml"
	@echo "  - bandit to find security issues in app code using bandit as configured in pyproject.toml"
	@echo "  - licensecheck to check dependencies licences compatibility with application license using licensecheck as configured in pyproject.toml"
	@echo "  - docs to produce documentation in html format using sphinx as configured in pyproject.toml"
	@echo "  - checks to run mypy, lint, bandit, licensecheck, tests and check formatting altogether"
	@echo "  - clean to remove cache file"
	@echo "  - docker_build to build docker image according to Dockerfile, tagged with app version"
	@echo "  - docker_run to run latest built docker image"
	@echo "------------------------------------"

$(pre_deps_tag):
ifndef POETRY_EXISTS
	@echo "Installing Poetry"
	curl -sSL https://install.python-poetry.org | python3 -
	which poetry
	poetry --version
	touch $(pre_deps_tag)
else
	@echo "Poetry already installed"
	poetry --version
	touch $(pre_deps_tag)
endif

$(setup_tag): $(pre_deps_tag) pyproject.toml
	@echo "==Setting up package environment=="
	poetry config virtualenvs.prefer-active-python true
	poetry lock --no-update
	poetry install --with unit --no-cache
	touch $(setup_tag)

requirements/requirements.txt: poetry.lock pyproject.toml
	mkdir -p requirements
	poetry export -f requirements.txt --output requirements/requirements.txt --without dev --without-hashes

reqs: requirements/requirements.txt

$(env_tag): $(pre_deps_tag) pyproject.toml
	@echo "==Setting up package environment=="
	poetry config virtualenvs.prefer-active-python true
	poetry lock --no-update
	poetry install --no-cache
	touch $(setup_tag)

setup: $(env_tag)

setup_dev: $(env_tag)
	poetry install --with dev --sync --no-cache

dist/.build-tag: $(files) pyproject.toml requirements/requirements.txt
	@echo "==Building package distribution=="
	poetry build
	ls -rt  dist/* | tail -1 > dist/.build-tag

dist: dist/.build-tag

$(install_tag): $(files) pyproject.toml requirements/requirements.txt
	@echo "==Installing package=="
	poetry install
	touch $(install_tag)

uninstall:
	@echo "==Uninstall package $(package_name)=="
	${PYTHON} pip uninstall -y $(package_name)
	${PYTHON} pip freeze | grep -v "@" | xargs ${PYTHON} pip uninstall -y
	rm -f $(env_tag) $(env_dev_tag) $(pre_deps_tag) $(install_tag)

install: $(install_tag)

format: setup_dev
	${PYTHON} black $(folders)
	${PYTHON} isort $(folders)

lint: setup_dev
	${PYTHON} flake8 $(folders)

mypy: setup_dev
	${PYTHON} mypy --install-types --non-interactive

tests: setup_dev
	${PYTHON} pytest tests

bandit: setup_dev
	${PYTHON} bandit -r -c pyproject.toml --severity-level high --confidence-level high .

licensecheck: setup_dev requirements/requirements.txt
	${PYTHON} licensecheck

checks: lint mypy bandit licensecheck tests
	${PYTHON} black --check $(folders)
	${PYTHON} isort $(folders) -c

docs: setup_dev $(doc_files) pyproject.toml
	sphinx-apidoc --implicit-namespaces -f -o sphinx/source/api py4ai
	make --directory=sphinx --file=Makefile clean html

clean:
	@echo "==Cleaning environment=="
	rm -rf docs
	rm -rf build
	rm -rf sphinx/source/api
	rm -rf requirements
	rm -rf $(shell find . -name "*.pyc") $(shell find . -name "__pycache__")
	rm -rf *.egg-info .mypy_cache .pytest_cache .make_cache $(env_tag) $(env_dev_tag) $(install_tag)

$(docker_build_tag): Dockerfile requirements/requirements.txt py4ai pyproject.toml
	@echo "==Building docker container=="
	TAG=$$(${PYTHON} py4ai/core/_version.py); \
	PYTHON_VERSION=$$(python --version); \
	PYTHON_VERSION="$${PYTHON_VERSION#Python }"; \
	PYTHON_VERSION="$${PYTHON_VERSION%.*}"; \
	docker build -t $(image_name):"$${TAG}" --build-arg PY_VERSION=$${PYTHON_VERSION} .; \
	VERSION=$$(cat $(docker_build_tag)); \
	if [[ "$${VERSION}" != "$${TAG}" ]]; then echo "==Updating docker version tag=="; echo "$${TAG}" > $(docker_build_tag); fi

docker_build: $(docker_build_tag)

docker_run: $(docker_build_tag)
	@echo "==Run detached docker image '$(project_name)' from '$(image_name):$$(cat $(docker_build_tag))' container=="
	docker run --rm -it --name $(project_name) $(image_name):$$(cat $(docker_build_tag))
