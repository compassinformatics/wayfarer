# cd D:\GitHub\wayfarer
# docker context use default
# docker build . --tag wayfarer
# docker run --publish 8000:8000 wayfarer
# docker exec -it wayfarer bash

FROM python:3.10-slim-buster

RUN pip3 install wayfarer

# add in the demo requirements
COPY requirements.demo.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/"

COPY ./demo /demo
COPY ./data /data
WORKDIR /demo

EXPOSE 8000
CMD uvicorn main:app --host 0.0.0.0 --port 8000

# http://localhost:8000/