FROM alpine:3.10

RUN apk update && \
  apk add --no-cache youtube-dl ffmpeg && \
  mkdir -p /opt/ytsync

RUN pip3 install requests

WORKDIR /opt/ytsync
COPY dp.py .

ENTRYPOINT [ "python3", "ytsync.py" ]
