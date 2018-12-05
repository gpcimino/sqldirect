VENV_NAME=.venv
VENV_ACTIVATE=$(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3
SYSPYTHON=/usr/bin/python3
PROJECT=sqldirect

venv: requirements.txt
	rm -rf ${VENV_NAME}; \
	${SYSPYTHON} -m venv ${VENV_NAME}; \
	. ${VENV_ACTIVATE} ;\
	pip install --upgrade pip; \
	pip install -Ur requirements.txt ;\
	pip install pylama; \
	pip install coverage; \
	pip install -e .;

#./${PROJECT}/*.py ./test/*.py
test: 
	. ${VENV_ACTIVATE}; \
	coverage run --omit=.venv/*,tests/*  -m unittest discover -s tests/; \
	coverage report;

quality:
	. ${VENV_ACTIVATE}; \
	pylama ./sqldirect/;

clean: clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	#name '*~' -exec rm --force  {}

clean-build:
	rm -Rf build/
	rm -Rf dist/
	rm -Rf *.egg-info

sdist:  ${PROJECT}/*.py
	python setup.py sdist

bdist:  ${PROJECT}/*.py
	python setup.py bdist_wheel --universal




