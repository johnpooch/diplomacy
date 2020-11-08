FROM python:latest AS diplomacy-base

ARG DOCKER_UID
ENV PATH="$PATH:/home/app/.local/bin"
ARG INSTALL_DIR=/opt/diplomacy
ENV INSTALL_DIR=$INSTALL_DIR
ENV PATH="$PATH:/home/app/.local/bin:$INSTALL_DIR/.bin"
ENV PYTHONUNBUFFERED 1

RUN useradd -u ${DOCKER_UID:-2000} -ms /bin/bash app
RUN install -d -g app -o app $INSTALL_DIR/.bin $INSTALL_DIR/diplomacy
RUN chown -R app:app $INSTALL_DIR/.bin
ADD --chown=app:app .docker/bin $INSTALL_DIR/.bin


FROM diplomacy-base AS diplomacy-deps

RUN install -d -g app -o app $INSTALL_DIR/.deps

USER app
WORKDIR $INSTALL_DIR/.deps

ADD --chown=app:app ./*requirements.txt $INSTALL_DIR/.deps/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM diplomacy-deps AS diplomacy-service

WORKDIR $INSTALL_DIR

COPY --from=diplomacy-deps --chown=app:app /home/app /home/app

WORKDIR "$INSTALL_DIR/diplomacy"
EXPOSE 8000
ENTRYPOINT ["start-service"]

FROM diplomacy-service AS diplomacy-worker

ENTRYPOINT ["start-worker"]
