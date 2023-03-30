FROM python:3.10 AS base
COPY ./gateway /gateway
COPY ./base_requirements.txt /gateway/base_requirements.txt
WORKDIR /gateway
RUN pip install -r base_requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8001