FROM jenkins/agent:alpine-jdk21

USER root

# Install Python 3.11
RUN apk add python3

RUN apk add py3-pip pipx

RUN apk add --no-cache pkgconfig glib-dev
RUN apk add --no-cache mysql-dev build-base  python3-dev
RUN pip wheel --no-cache-dir --use-pep517 "mysqlclient (==2.2.7)"

RUN python3 --version

# Ensure pipx installs globally in /opt
ENV PIPX_BIN_DIR="/opt/poetry/bin"
ENV PIPX_HOME="/opt/poetry"

# Install Poetry using pipx
RUN pipx install poetry

# Ensure Poetry is in the global PATH
ENV PATH="${PIPX_BIN_DIR}:${PATH}"

# Change ownership so Jenkins user can access Poetry
RUN chown -R jenkins:jenkins /opt/poetry

# Verify Poetry installation as root
RUN poetry --version

# Switch to Jenkins user
USER jenkins

# Verify Poetry installation as Jenkins user
RUN poetry --version

WORKDIR /home/jenkins/poetry/

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root --no-interaction

RUN pipx install uvicorn

WORKDIR /home/jenkins/workspace/membership_management/
# COPY ./app /home/jenkins/workspace/membership_management/app