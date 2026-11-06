# syntax=docker/dockerfile:1
# ---------------------------------------------------------------
# e-financeiro — imagem multi-stage (compila o mysqlclient e
# depois gera uma imagem final leve, só com as bibliotecas de runtime)
# ---------------------------------------------------------------

# ---------- Estágio 1: construir as wheels ----------
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Estágio 2: imagem final ----------
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libmariadb3 = biblioteca de runtime exigida pelo mysqlclient
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmariadb3 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia tudo que o Python instalou no estágio do builder
COPY --from=builder /install /usr/local

COPY requirements.txt .
COPY manage.py .
COPY core/ core/
COPY web/ web/
COPY cadastros/ cadastros/
COPY financeiro/ financeiro/
COPY templates/ templates/
COPY static/ static/

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENV PYTHONPATH=/app

ENTRYPOINT ["/entrypoint.sh"]
