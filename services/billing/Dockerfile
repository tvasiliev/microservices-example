FROM python:3.11 AS base
COPY ./billing /billing
COPY ./modules /billing/modules
COPY ./base_requirements.txt /billing/base_requirements.txt
WORKDIR /billing
RUN pip install -r base_requirements.txt
RUN pip install -r requirements.txt