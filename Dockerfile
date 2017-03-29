FROM plone:4
MAINTAINER "Timo Stollenwerk" <tisto@plone.org>

COPY site.cfg /plone/instance/
RUN bin/buildout -c site.cfg
