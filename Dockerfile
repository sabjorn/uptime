FROM python:3.10-slim

WORKDIR /usr/src/app

COPY uptime.py uptime.py

RUN pip install --no-cache-dir requests

CMD ["python3", "./uptime.py"]
