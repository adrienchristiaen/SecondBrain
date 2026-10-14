test:
	PYTHONPATH=06-tools python3 -m unittest discover -s 06-tools/phoenix_cli/tests -t 06-tools

dashboard:
	./phoenix dashboard serve --sync
