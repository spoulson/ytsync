# Base image.
FROM alpine:3.10 AS base
RUN apk update && \
  apk add --no-cache python3 && \
  mkdir -p /opt/ytsync

# Build stage.
FROM base AS build
WORKDIR /opt/ytsync
COPY . .
RUN pip3 install wheel && \
  python3 setup.py bdist_wheel

# Production stage.
FROM base AS production
COPY --from=build /opt/ytsync/dist /opt/ytsync/dist
RUN apk add --no-cache youtube-dl ffmpeg && \
  pip3 install -f /opt/ytsync/dist ytsync && \
  rm -rf /opt/ytsync

ENTRYPOINT [ "ytsync" ]
