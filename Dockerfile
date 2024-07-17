FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python3.10 -m pip install -r requirements.txt

COPY scripts /scripts

COPY . /srv/root
WORKDIR /srv/root

RUN chmod +x -R /scripts
ENTRYPOINT ["/scripts/bootstrap.sh"]