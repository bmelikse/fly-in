PY = python3
MAIN = main.py
MENU = menu.py
CONFIG ?= maps/easy/01_linear_path.txt

run:
	$(PY) $(MAIN) $(CONFIG)

menu:
	$(PY) $(MENU)

install:
	pip install -r requirements.txt

debug:
	$(PY) -m pdb $(MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . --warn-return-any \
		--warn-unused-ignores \
		--disallow-untyped-defs \
		--ignore-missing-imports \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: run menu install debug lint lint-strict clean