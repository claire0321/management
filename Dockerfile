FROM python:3.11.7

WORKDIR /fastapi-app

RUN pip install -U pip && pip install poetry

COPY poetry.lock pyproject.toml README.md /fastapi-app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction

RUN poetry check

COPY ./app ./app

CMD [ "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]