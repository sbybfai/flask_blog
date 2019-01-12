FROM python:3.6-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk add --no-cache mariadb-dev build-base
ENV FLASK_APP flasky.py
ENV FLASK_CONFIG production

RUN adduser -D flasky
USER flasky

WORKDIR /home/flasky
COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY flasky.py config.py boot.sh ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
