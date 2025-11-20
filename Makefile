SHELL := $(shell echo $$SHELL)

.PHONY: setup clean

setup:
	@echo "Checking for virtual environment..."
	@if [ ! -d ".venv" ]; then \
		echo "virtual environment not found. Creating and installing dependencies..."; \
		python -m venv .venv; \
		.venv/bin/python -m pip install --upgrade pip; \
		.venv/bin/python -m pip install -r requirements.txt; \
		echo "Setup complete!"; \
	else \
		echo "virtual environment already exists. To reinstall, run 'make clean setup'."; \
	fi

clean:
	@echo "Removing virtual environment and temporary files..."
	@rm -rf .venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete