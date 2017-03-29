FROM plone:4
MAINTAINER "Timo Stollenwerk" <tisto@plone.org>

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends  build-essential \
 && rm -rf /var/lib/apt/lists/*
USER plone

COPY site.cfg /plone/instance/
RUN bin/buildout -c site.cfg
