# 專案 Makefile（使用自訂配方前綴，避免 tab 問題）
.RECIPEPREFIX := >
PYTHON ?= python3
export PYTHONPATH := $(PWD)/src

.PHONY: validate health compare validate-ci

health:
> @echo "Python: $$($(PYTHON) -V)"
> @echo "PYTHONPATH=$(PYTHONPATH)"
> @echo "Checking files..."
> @test -f tools/validate_strategy.py || (echo "missing tools/validate_strategy.py" && exit 1)
> @test -f tests/resources/strategies/test_samples.json || (echo "missing test_samples.json" && exit 1)
> @test -f src/app/domain/strategies/validation.py || (echo "missing validation.py" && exit 1)

validate: health
> @echo "Running strategy schema validation against test samples..."
> $(PYTHON) tools/validate_strategy.py tests/resources/strategies/test_samples.json | tee validation_report.json
> @echo "Validation report saved to validation_report.json"

compare:
> @diff -u tests/resources/strategies/expected_report.json validation_report.json || (echo "\nDiff found. If intentional, update expected_report.json" && exit 1)

validate-ci: validate compare
> @echo "All good ✔"
