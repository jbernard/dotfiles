test:
	@cd tests && PYTHONPATH=../ py.test

publish-test:
	@python setup.py sdist upload -r test
	@python setup.py bdist_wheel upload -r test

publish-pypi:
	@python setup.py sdist upload -r pypi
	@python setup.py bdist_wheel upload -r pypi

.PHONY: test publish-test publish-pypi
