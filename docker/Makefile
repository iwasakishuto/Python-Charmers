help:
	@cat Makefile

DATA?="${HOME}/Data"
DOCKER_FILE=docker-compose.yml
DOCKER=docker-compose
HOST_PORT=8888
SRC?=$(shell dirname `pwd`)

build:
	cp ../poetry.lock ../pyproject.toml .
	$(DOCKER) build --build-arg pycharmers
	rm poetry.lock pyproject.toml

rebuild:
	$(DOCKER) build --build-arg --no-cache pycharmers

bash: build
	$(DOCKER) run -v $(SRC):/src/workspace -v $(DATA):/data pycharmers bash

ipython: build
	$(DOCKER) run -v $(SRC):/src/workspace -v $(DATA):/data pycharmers ipython

notebook: build
	$(DOCKER) run -p $(HOST_PORT):8888 -v $(SRC):/src/workspace -v $(DATA):/data pycharmers
