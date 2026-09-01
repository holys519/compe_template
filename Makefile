PYTHON ?= python3

.PHONY: status test report

status:
	$(PYTHON) scripts/status.py

test:
	$(PYTHON) -m unittest discover -s tests -v

report:
	$(PYTHON) scripts/report.py
