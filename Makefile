.PHONY: default
default: lint

.PHONY: init
init:
	@if [ ! -e .git/hooks/pre-commit ]; then \
		mkdir -p .git/hooks; \
		cp -r hooks .git/; \
	fi

.PHONY: lint
lint: init
	pylint ytsync

.PHONY: tools
tools: init
	pip3 install pylint

.PHONY: clean
clean: init
	rm -rf build dist *.egg-info
