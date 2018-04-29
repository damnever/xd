upload: clean
	python setup.py bdist_wheel sdist
	twine upload dist/*


clean:
	find . -type f -name '*.pyc' -exec rm -f {} +
	find . -type f -name '*.pyo' -exec rm -f {} +
	find . -type f -name '*.~' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf build xd.egg-info dist
