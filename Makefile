test:
	@PYTHONPATH=$$PWD py.test

publish:
	@python setup.py sdist upload -r pypi
	@python setup.py bdist_wheel upload -r pypi

.PHONY: test publish
