FROM python:3.11.7

RUN pip install -U pip && pip install poetry

WORKDIR /fastapi-app

COPY poetry.lock pyproject.toml README.md /fastapi-app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction

RUN poetry check

COPY ./app ./app

RUN pip install uvicorn

CMD [ "poetry", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0" ]