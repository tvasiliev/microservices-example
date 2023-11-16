FROM python:3.11 AS base
COPY ./tasks /tasks
COPY ./modules /tasks/modules
COPY ./base_requirements.txt /tasks/base_requirements.txt
WORKDIR /tasks
RUN pip install -r base_requirements.txt
RUN pip install -r requirements.txt