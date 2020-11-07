FROM python:latest AS diplomacy-base

ARG DOCKER_UID
ARG ENV=prod
ARG INSTALL_DIR=/opt/diplomacy

ENV ENV=$ENV
ENV INSTALL_DIR=$INSTALL_DIR
ENV PATH="$PATH:/home/app/.local/bin:$INSTALL_DIR/.bin"
ENV PYTHONUNBUFFERED 1

RUN useradd -u ${DOCKER_UID:-2000} -ms /bin/bash app
ADD --chown=app:app .docker/bin $INSTALL_DIR/.bin

WORKDIR /code
COPY . /code

FROM diplomacy-base AS diplomacy-deps

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM diplomacy-deps AS diplomacy-service

EXPOSE 8000
ENTRYPOINT ["start-service"]

FROM diplomacy-deps AS diplomacy-worker

EXPOSE 8000
ENTRYPOINT ["start-worker"]
