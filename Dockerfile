FROM python:3.10-alpine

USER root

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8050

ENV NAME World

CMD ["python", "app.py"]