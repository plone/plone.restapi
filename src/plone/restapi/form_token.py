"""Single-use form tokens with a minimum age, kept in memcached.

A form gets a token from the ``@form-token`` endpoint when it is shown, and
the endpoint that handles the form only accepts it once, and only after
FORM_TOKEN_MIN_AGE seconds: bots post at once, people need time to fill in a
form.  Scripts that post to the endpoint directly have no token at all.  This
works next to a captcha, if the form has one.

``@email-notification`` checks the token of the contact form, and add-ons can
check one with ``verify_token`` for their own forms.

It is only enabled when pymemcache is installed and FORM_TOKEN_MEMCACHE names
the memcached servers.  Otherwise forms work as before, without tokens.

The tokens are kept in memcached instead of the ZODB, because issuing one is a
write on a GET request.
"""

from plone.restapi import _
from zExceptions import BadRequest
from zope.i18n import translate

import logging
import os
import re
import secrets
import threading
import time

try:
    from pymemcache.client.hash import HashClient
except ImportError:
    HashClient = None


logger = logging.getLogger(__name__)

KEY_PREFIX = "plone.restapi.form_token."
# secrets.token_urlsafe(32): this also keeps other input out of the memcached
# protocol.
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")

TOKEN_VALID = "valid"
# Missing, unknown, expired or used before.
TOKEN_INVALID = "invalid"
# Used within FORM_TOKEN_MIN_AGE seconds: what bots do.
TOKEN_TOO_NEW = "too-new"

_local = threading.local()


def get_servers():
    """memcached servers from FORM_TOKEN_MEMCACHE, like "memcached:11211"."""
    servers = []
    for server in os.environ.get("FORM_TOKEN_MEMCACHE", "").split():
        host, _sep, port = server.rpartition(":")
        servers.append((host, int(port)) if host else (port, 11211))
    return servers


def is_enabled():
    return HashClient is not None and bool(get_servers())


def get_min_age():
    return int(os.environ.get("FORM_TOKEN_MIN_AGE", "15"))


def get_lifetime():
    return int(os.environ.get("FORM_TOKEN_LIFETIME", "3600"))


def get_client():
    """A memcached client per thread: pymemcache clients are not thread-safe."""
    client = getattr(_local, "client", None)
    if client is None:
        client = HashClient(
            get_servers(), connect_timeout=1, timeout=1, ignore_exc=True
        )
        _local.client = client
    return client


def issue_token():
    """Return a new token, or None when memcached cannot store it."""
    token = secrets.token_urlsafe(32)
    stored = get_client().set(
        KEY_PREFIX + token, str(int(time.time())), expire=get_lifetime(), noreply=False
    )
    if not stored:
        logger.error("Cannot store a form token in memcached %s", get_servers())
        return None
    return token


def redeem_token(token):
    """Use up the token, and return TOKEN_VALID, TOKEN_INVALID or TOKEN_TOO_NEW.

    A token that is used too early is used up as well, so a bot has to get a
    new one and wait again.
    """
    if not isinstance(token, str) or not TOKEN_PATTERN.match(token):
        return TOKEN_INVALID
    client = get_client()
    key = KEY_PREFIX + token
    issued = client.get(key)
    # memcached answers DELETED to only one request for a key, so two requests
    # with the same token cannot both be accepted.
    if not client.delete(key, noreply=False) or issued is None:
        return TOKEN_INVALID
    if time.time() - int(issued) < get_min_age():
        return TOKEN_TOO_NEW
    return TOKEN_VALID


def log_spam_blocked(reason, form):
    """Log a submission that was stopped, so it can be counted, for example in
    Loki: ``|= "Spam blocked" | regexp "reason=(?P<reason>[a-z-]+)"``.

    Without the form data or the client address: the access log of the proxy
    has the address of the POST at the same time.
    """
    logger.info("Spam blocked: reason=%s form=%s", reason, form)


def verify_token(request, token, form):
    """Raise BadRequest unless the token of the submission is valid.

    ``form`` names the form in the log, like "@email-notification".
    """
    status = redeem_token(token)
    if status == TOKEN_TOO_NEW:
        log_spam_blocked("early-token", form)
    # One answer for a missing, unknown, used or too new token, so bots cannot
    # tell what is wrong.
    if status != TOKEN_VALID:
        raise BadRequest(
            translate(
                _("form_token_error", default="Invalid request."), context=request
            )
        )
