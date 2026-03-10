PYTHON := python3
PYTHONPATH := src

.PHONY: test demo invalid

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_pet.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_invalid_pet.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_metrics.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_cli_metrics.py
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_cli_metrics_json.py

invalid:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tests/test_invalid_pet.py

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py 72
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py --json 72
