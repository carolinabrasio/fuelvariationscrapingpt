.PHONY: test

test:
	@set -eu; \
	venv="$$(mktemp -d "$${TMPDIR:-/tmp}/fuelvariationscrapingpt-tests.XXXXXX")"; \
	trap 'rm -rf "$$venv"' EXIT INT TERM; \
	python3 -m venv "$$venv"; \
	"$$venv/bin/python" -m pip install -r requirements_test.txt; \
	"$$venv/bin/python" -m pytest -q
