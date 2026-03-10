PYTHON := python3
PYTHONPATH := src

.PHONY: test demo

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py 72
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py --json 72
