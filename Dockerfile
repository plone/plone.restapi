FROM plone:4
MAINTAINER "Timo Stollenwerk" <tisto@plone.org>

USER root
RUN apt-get update && apt-get install -y git
USER plone

COPY site.cfg /plone/instance/
RUN bin/buildout -c site.cfg
