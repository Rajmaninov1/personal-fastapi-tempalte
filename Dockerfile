FROM python:3.11-alpine3.19

WORKDIR /usr/src/workspace

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update

COPY Pipfile Pipfile.lock ./

RUN python -m pip install pipenv \
  && pipenv install --system --deploy

WORKDIR ./app

COPY /app ./

EXPOSE 4003

CMD ["python", "main.py"]
