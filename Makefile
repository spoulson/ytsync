.PHONY: default
default: lint mypy pycodestyle

.PHONY: init
init:
	@if [ ! -e .git/hooks/pre-commit ]; then \
		mkdir -p .git/hooks; \
		cp -r githooks/* .git/hooks; \
	fi

.PHONY: lint
lint: init
	pylint ytsync

.PHONY: mypy
mypy: init
	mypy ytsync

.PHONY: pycodestyle
pycodestyle: init
	pycodestyle ytsync

.PHONY: tools
tools: init
	pip3 install pylint mypy pycodestyle

.PHONY: clean
clean: init
	rm -rf build dist *.egg-info
