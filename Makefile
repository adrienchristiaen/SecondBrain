test:
	PYTHONPATH=06-tools python3 -m unittest discover -s 06-tools/iris_cli/tests -t 06-tools

dashboard:
	./iris dashboard serve --sync
