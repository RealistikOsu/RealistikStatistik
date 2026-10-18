FROM python:3.10-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt


FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

COPY --chmod=755 scripts /scripts

COPY . /srv/root
WORKDIR /srv/root

ENTRYPOINT ["/scripts/bootstrap.sh"]
