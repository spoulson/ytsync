.PHONY: default
default: init lint

.PHONY: init
init:
	@if [ ! -e .git/hooks/pre-commit ]; then \
		mkdir -p .git/hooks; \
		cp -r hooks .git/; \
	fi

.PHONY: lint
lint:
	pylint ytsync scripts
