.PHONY: audit report apply-fixes test

audit:
	UV_INDEX_URL=https://pypi.org/simple uvx --no-config --from agentops-cockpit agent-ops report

report: audit

apply-fixes:
	UV_INDEX_URL=https://pypi.org/simple uvx --no-config --from agentops-cockpit agent-ops report --apply-fixes

test:
	./.venv/bin/python -m pytest tests/
