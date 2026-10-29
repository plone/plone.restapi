# Build environment for Anthropic OSS Scanner (plone.restapi).
# Assumes the build context is the root of a plone.restapi checkout.
# Network is available during this build only; the audit runs offline,
# so everything needed for building and running tests is installed here.
FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates \
    libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libpng-dev \
    libffi-dev libssl-dev libbz2-dev \
    && rm -rf /var/lib/apt/lists/*

# Plone 6.2 pinned versions set (official constraints).
ARG PLONE_CONSTRAINTS=https://dist.plone.org/release/6.2-latest/constraints.txt
RUN curl -fsSL "$PLONE_CONSTRAINTS" -o /tmp/constraints.txt \
    # plone.restapi itself is installed from source below; drop its pin
    && sed -i '/^plone\.restapi==/d' /tmp/constraints.txt

WORKDIR /src
COPY . /src

# Install Plone + plone.restapi (editable) with test dependencies.
RUN pip install --upgrade pip wheel setuptools \
    && pip install -c /tmp/constraints.txt Products.CMFPlone \
    && pip install -c /tmp/constraints.txt -e ".[test]" \
    && pip install -c /tmp/constraints.txt zope.testrunner pytest

# Sanity check: package imports and the test layer module loads.
RUN python -c "import plone.restapi, plone.restapi.testing; print('ok')"

# Running tests (offline):
#   zope-testrunner --test-path=src -s plone.restapi -t test_services_users
# or:
#   pytest src/plone/restapi/tests -k users
