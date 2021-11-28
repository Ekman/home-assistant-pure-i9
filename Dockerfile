FROM python:3-alpine

ENV FILES_DIR="/files"

ADD requirements.txt "$FILES_DIR/"

RUN mkdir -p /files \
    && apk add --update --no-cache gcc musl-dev libffi-dev \
    && pip install --requirement "$FILES_DIR/requirements.txt" --no-compile --no-clean --disable-pip-version-check

WORKDIR "$FILES_DIR"
ENTRYPOINT ["sh"]
VOLUME ["$FILES_DIR"]
