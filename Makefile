.PHONY: help spotlight validate test diff status

help:
	@echo "Physicist Spotlight"
	@echo
	@echo "Available commands:"
	@echo "  make spotlight DATE=09/15/2026   Run the research workflow"
	@echo "  make test        Run tests with temporary data and a fake model"
	@echo "  make validate    Run local CSV validation"
	@echo "  make diff        Show changes made to the repository"
	@echo "  make status      Show Git status"

spotlight:
	@bash scripts/run_spotlight.sh "$(DATE)"

validate:
	@python3 scripts/check_duplicate.py
	@python3 scripts/validate_csv.py

diff:
	@git diff

status:
	@git status

test:
	@python3 -m unittest discover -s tests -v
