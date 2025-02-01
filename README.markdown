# Ollama Webhooks

An attempt at providing webhook support for Ollama.

Configure your Ollama client to send requests to this web server, and the request will enter a queue.

The requests in that queue will be sent to Ollama, and once processed, a request will be sent back to the configured webhook URL.

This is a proof-of-concept at the moment which I'm using in a small self-hosted project.

## Getting started for local development

To run the site locally, create a local virtual environment (you can do this using `make pyenv-virtualenv` if you use [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)), and then run:

- `make .env` to write a default `.env` file;
- `make db` to create a database;
- `pip install --requirement requirements.txt` to install Python packages;
- `python manage.py migrate` to apply database migrations;
- `python manage.py runserver` to start the website.

This repo includes a [pre-commit](https://pre-commit.com/) configuration. Run `pre-commit install` to set up a hook which will run appropriate linters and auto-formatters across your code before you make a commit.
