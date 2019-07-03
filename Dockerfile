FROM python:3.5-slim

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV LISTEN_IP 0.0.0.0
ENV LISTEN_PORT 80
ENV AWS_REGION eu-central-1

CMD ["python", "app.py"]
