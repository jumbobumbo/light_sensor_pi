FROM python:3.8.3-slim-buster

# UPDATE/UPGRADE PACKAGES AND PIP
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install build-essential -y \
    && pip3 install --upgrade pip

# INSTALL REQUIREMENTS
COPY requirements.txt /
RUN pip3 install -r requirements.txt

# CREATE APP DIR AND COPY
RUN mkdir app
COPY app /app
