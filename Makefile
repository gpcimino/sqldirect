test:
	python -m unittest discover -s ./tests/

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	#name '*~' -exec rm --force  {}

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

sdist:
	python setup.py sdist

bdist:
	python setup.py bdist_wheel --universal

postgres:
	export SQLDIRECT_CONN_STR="postgresql://postgres:password@localhost/sqldirect"
	docker run -d -p 5432:5432 --name postegresql -e POSTGRES_PASSWORD=password -e POSTGRES_DB=sqldirect --rm postgres:10.5

rebuild-venv:
	rm -rf ./venv/
	python36 -m venv ./venv/
	source ./venv/bin/activate
	pip install -r requirements.txt

quality:
	pylama ./sqldirect/

