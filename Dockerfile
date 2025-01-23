FROM python:3.11.7

RUN pip install -U poetry

WORKDIR /fatapi-app

COPY poetry.lock pyproject.toml /fatapi-app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction


COPY ./app ./app

CMD [ "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]

#FROM python:3.11.7
#
#RUN pip3 install --upgrade pip3
#RUN pip3 install poetry
#
#WORKDIR /fastapi-management
#
#COPY pyproject.toml poetry.lock ./
#COPY ./app /fastapi-management/app
#
#RUN poetry install --no-root
##EXPOSE 8000
#CMD [ "poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
##ENTRYPOINT poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
##ENTRYPOINT[ "poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0" ]