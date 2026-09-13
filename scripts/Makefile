.PHONY: help spotlight validate diff status

help:
	@echo "Physicist Spotlight"
	@echo
	@echo "Available commands:"
	@echo "  make spotlight   Run the complete Codex research workflow"
	@echo "  make validate    Run local CSV validation"
	@echo "  make diff        Show changes made to the repository"
	@echo "  make status      Show Git status"

spotlight:
	@./scripts/run_spotlight.sh

validate:
	@python3 scripts/check_duplicate.py
	@python3 scripts/validate_csv.py

diff:
	@git diff

status:
	@git status