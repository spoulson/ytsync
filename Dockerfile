FROM alpine
RUN apk add -U --no-cache python3 py3-pip ffmpeg gcc musl-dev
WORKDIR /opt/ytsync
COPY . .
RUN pip3 install wheel
RUN python3 setup.py bdist_wheel
RUN pip3 install -f /opt/ytsync/dist ytsync

# Clean up.
RUN cd /; rm -rf /opt/ytsync
RUN apk del gcc musl-dev

ENTRYPOINT [ "ytsync" ]
