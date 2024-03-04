FROM python:3.10-slim as builder

WORKDIR /dnd

COPY . .

RUN pip install --no-cache-dir discord.py

FROM alpine:latest

RUN apk update && apk add --no-cache python3 py3-pip

WORKDIR /dnd

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /dnd /dnd


RUN ["python3", "main.py"]
