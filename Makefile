.PHONY: help
help: ## Display this help screen.
	@grep -E '^\S.+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-45s\033[0m %s\n", $$1, $$2}'

.PHONY: db
db:  ## Create a database.
	createuser ollama_webhooks --createdb
	psql --command "alter user ollama_webhooks with encrypted password 'security_is_important';"
	createdb ollama_webhooks --owner=ollama_webhooks

.PHONY: db-delete
db-delete:  ## Delete database.
	dropdb ollama_webhooks --if-exists
	dropdb test_ollama_webhooks --if-exists
	seq 0 $$(getconf _NPROCESSORS_ONLN) | xargs -I % dropdb test_ollama_webhooks_gw% --if-exists
	dropuser ollama_webhooks --if-exists

.PHONY: pyenv-virtualenv
pyenv-virtualenv:  ## Create a virtual environment managed by pyenv-virtualenv.
	pyenv virtualenv `pyenv latest --known 3` ollama-webhooks
	echo "ollama-webhooks" > .python-version

.PHONY: pyenv-virtualenv-delete
pyenv-virtualenv-delete:  ## Delete a virtual environment managed by pyenv-virtualenv.
	pyenv virtualenv-delete --force `cat .python-version || echo ollama-webhooks`
	rm -f .python-version

.env:  ## Create .env file suitable for development.
	printf "ALLOWED_HOSTS=localhost 127.0.0.1\nCELERY_BROKER_USE_SSL=\nDEBUG=1\nDATABASE_URL=postgres://ollama-webhooks:security_is_important@localhost/ollama-webhooks\nCELERY_BROKER_URL=redis://localhost:6379/0\nOLLAMA_HOST=http://localhost:11434\nROOT_LOG_HANDLERS=rich\nROOT_LOG_LEVEL=DEBUG\nSECURE_HSTS_SECONDS=0\nSECURE_SSL_REDIRECT=\nSENTRY_DEBUG=\nSENTRY_ENVIRONMENT=`whoami`\n# SENTRY_DSN=\n" > .env

requirements.txt: requirements.in;
	pip-compile --allow-unsafe --generate-hashes --strip-extras

.PHONY: containers
containers: ## Make containers from the current code, tagged so they'll be used with docker compose.
	docker build --target web --tag ghcr.io/craiga/ollama-webhooks/web:latest .
	docker build --target worker --tag ghcr.io/craiga/ollama-webhooks/worker:latest .

.PHONY: all clean test
