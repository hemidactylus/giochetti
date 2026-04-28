SHELL := /bin/bash

.PHONY: all check typecheck stylecheck format stylefix

all: help

check: stylecheck typecheck

format:
	uv run ruff format egame *.py

typecheck:
	uv run mypy egame *.py

stylecheck:
	uv run ruff check egame *.py
	uv run ruff format --check egame *.py

stylefix:
	uv run ruff check egame *.py --fix

lc:
	find -iname "*.py" | grep -v ".venv" | grep -v "voice-rec" | xargs cat | wc -l

help:
	@echo "======================================================================"
	@echo "make command                     purpose"
	@echo "----------------------------------------------------------------------"
	@echo "typecheck                        run mypy typecheck"
	@echo "stylecheck                       lint and format checks"
	@echo "check                            alias for: typecheck + stylecheck"
	@echo "format                           actual reformat (changes files)"
	@echo "stylefix                         auto-fix style wherever possible"
	@echo "======================================================================"