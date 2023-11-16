FROM python:3.11 AS base
COPY ./gateway /gateway
COPY ./modules /gateway/modules
COPY ./base_requirements.txt /gateway/base_requirements.txt
WORKDIR /gateway
RUN pip install -r base_requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8001