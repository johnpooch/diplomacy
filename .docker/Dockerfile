FROM python:latest
ENV PYTHONUNBUFFERED 1

ENV PATH="$PATH:/home/app/.local/bin"

WORKDIR /code
COPY . /code

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT .docker/deploy/start.sh
