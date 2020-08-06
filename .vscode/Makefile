# vim: ft=make

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

freeze-extensions: ## Freeze VS Code Extensions
	@code --list-extensions | sort > extensions.txt

install-extensions: ## Installed previously frozen extensions
	@cat extensions.txt | xargs -L 1 code --install-extension

install-mono-fonts: ## Install Mono-Spaced fonts for IDE
	@./mono-install

install: install-mono-fonts install-extensions ## Install mono-fonts and VS Code Extensions
