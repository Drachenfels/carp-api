define clean_old_files
	rm -rf build/
	rm -rf dist/*
	rm -rf carp_api.egg-info/

	python3 setup.py clean
endef


publish-test:
	$(call clean_old_files)

	python3 setup.py sdist bdist_wheel

	twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose


publish-production:
	$(call clean_old_files)

	python3 setup.py sdist bdist_wheel

	twine upload dist/*


.PHONY: tests
