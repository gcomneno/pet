.PHONY: test demo validate clean

PYTHON := python3

test:
	$(PYTHON) test_pet.py

demo:
	$(PYTHON) pet.py 136
	@echo
	$(PYTHON) pet.py --json 27398

validate:
	$(PYTHON) pet.py --validate pet136.json

clean:
	rm -f *.pyc
	rm -rf __pycache__
