# Matches the runtime of the docker-compose setup (Python 3.10, pandas 2.x).
FROM python:3.10-slim-bookworm

# Home Assistant builds with this directory as the context, so the miner
# source is fetched from GitHub instead of copied from the repo root.
ARG MINER_REPO=https://github.com/spencer012/Twitch-Channel-Points-Miner-v2
ARG MINER_REF=feature/post-origin-switch-work

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/usr/src/app \
    TERM=xterm-256color

WORKDIR /usr/src/app

ADD ${MINER_REPO}/archive/refs/heads/${MINER_REF}.tar.gz /tmp/miner.tar.gz
RUN tar -xzf /tmp/miner.tar.gz --strip-components=1 -C /usr/src/app \
  && rm /tmp/miner.tar.gz \
  && pip install --no-cache-dir -r requirements.txt

COPY launcher.py /launcher.py

CMD [ "python", "/launcher.py" ]
