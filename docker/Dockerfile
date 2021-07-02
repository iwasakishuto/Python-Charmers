FROM jupyter/scipy-notebook

LABEL org.opencontainers.image.authors="cabernet.rock@gmail.com"

USER root

ENV PYTHONUNBUFFERED=1

WORKDIR /playground

COPY poetry.lock pyproject.toml ./

RUN echo "deb http://security.ubuntu.com/ubuntu bionic-security main" >> /etc/apt/sources.list \
 && apt-get update --fix-missing \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends \
      vim \
      cmake \
      g++ \
      git \
      build-essential \
      xorg \
      libssl1.0-dev \      
      libxrender-dev \
      unzip \
      gdebi \
      wget \
      xvfb \
      libfontconfig \
 && apt-get autoremove -y \
 && apt-get clean -y \
 && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-dev --remove-untracked

WORKDIR /data

CMD jupyter notebook --port=8888 --ip=0.0.0.0