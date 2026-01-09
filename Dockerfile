FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml ./

RUN poetry install

COPY ./src ./

ENV HD_HOST="0.0.0.0"
ENV HD_PORT="8888"
ENV HD_PRODUCTION="true"

EXPOSE 8888

CMD ["poetry", "run", "python", "main.py"]