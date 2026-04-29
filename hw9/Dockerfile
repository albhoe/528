FROM python:3.13-slim-trixie

ENV env_variable=value
ENV GCE_METADATA_MTLS_MODE=none

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install requests

WORKDIR /app
COPY . .

CMD ["python","server.py"]