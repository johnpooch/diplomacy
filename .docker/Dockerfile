FROM python:latest
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY . /code

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT .docker/deploy/start.sh
