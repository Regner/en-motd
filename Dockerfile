

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

RUN apt-get update -qq
RUN apt-get upgrade -y -qq
RUN apt-get install -y -qq python-dev python-pip
RUN pip install -qU pip

ENV GOOGLE_APPLICATION_CREDENTIALS "path-to-credentials.json"
ENV GCLOUD_DATASET_ID "your gce project"

ADD en_motd.py /en_motd/
ADD requirements.txt /en_motd/

WORKDIR /en_motd/

RUN pip install -r requirements.txt

CMD python /en_motd/en_motd.py
