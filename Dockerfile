FROM python:3-alpine

ENV USER="purei9"
ENV USER_HOME="/home/$USER"
ENV FILES_DIR="$USER_HOME/files"

ADD requirements.txt "$FILES_DIR/"

RUN adduser -DSh "$USER_HOME" "$USER" \
    && mkdir -p "$FILES_DIR" \
    && apk add --update --no-cache gcc musl-dev libffi-dev \
    && pip install --requirement "$FILES_DIR/requirements.txt" --no-compile --no-clean --disable-pip-version-check

USER "$USER"
WORKDIR "$FILES_DIR"
ENTRYPOINT ["sh"]
VOLUME ["$FILES_DIR", "$USER_HOME/.cache", "/tmp"]
