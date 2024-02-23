FROM continuumio/miniconda3

RUN useradd -d /app -m -s /bin/bash python
RUN chown -R python:python /opt/conda

RUN apt update 2>/dev/null  \
    && apt-get install -qq sudo 2>/dev/null  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN echo "python ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/python

USER python

ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="/app/.local/bin:$POETRY_HOME/bin:$PATH"

WORKDIR /app

RUN conda init bash
RUN conda create -n app -q -y python=3.11
RUN echo "conda activate app" >> ~/.bashrc
#SHELL ["conda", "run", "-n", "app", "/bin/bash", "-c"]

RUN pip install --upgrade pip && pip install poetry && poetry self add "poetry-dynamic-versioning[plugin]"

#ARG GITHUB_USER
#ARG GITHUB_TOKEN

COPY pyproject.toml poetry.lock noxfile.py README.md  /app/
COPY .git/ /app/.git
COPY franknpython /app/franknpython

RUN sudo chown -R python:python .git README.md franknpython noxfile.py poetry.lock pyproject.toml

##RUN git config --global url."https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
RUN poetry install
RUN nox
RUN conda clean -ay

COPY scripts/ /app/scripts
RUN sudo chown -R python:python scripts

ENTRYPOINT ["python","scripts/run_stuff.py"]
