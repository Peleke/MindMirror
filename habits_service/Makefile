SHELL := /bin/bash

export PYTHONPATH=$(PWD)

alembic.rev:
	@alembic -c alembic.ini revision -m "$(msg)"

alembic.up:
	@alembic -c alembic.ini upgrade ${rev}

alembic.init:
	@alembic -c alembic.ini revision -m "init"


