"""A ``sphinxcontrib-httpexample`` builder for plone-client.

`plone-client <https://github.com/plone/plone-client>`_ is a Python library
for Plone sites. Its generic methods take a path that starts at the site root,
so every recorded request translates mechanically into one call:

* ``GET`` with JSON answers becomes ``client.get(path, **params)``;
* ``POST``, ``PATCH``, ``PUT`` and ``DELETE`` with a JSON body become
  ``client.post(path, data)`` and so on;
* anything else (extra headers on a ``GET``, a body that is not JSON, ``HEAD``,
  ``OPTIONS``, an answer that is not JSON) becomes ``client.request(...)``.

The client sends ``Accept: application/json``, the JSON ``Content-Type`` and
its own credentials, so those headers are left out.
"""

from sphinxcontrib.httpexample.parsers import HTTPRequest
from typing import Any
from urllib.parse import parse_qsl
from urllib.parse import urlsplit

import json
import keyword

#: Path of the site in the recorded requests.
SITE_ROOT = "/plone"
#: Methods with a generic method of their own.
GENERIC = {"GET", "POST", "PATCH", "PUT", "DELETE"}
#: Headers the client sends by itself.
IMPLICIT_HEADERS = {"host", "authorization"}
#: Width of a line of the generated code.
WIDTH = 79
INDENT = "    "


def site_path(path: str) -> str:
    """The path of a request, relative to the site root.

    :param path: Path of the recorded request, without a query string.
    :returns: A path that starts with ``/``.
    """
    if path == SITE_ROOT or path.startswith(f"{SITE_ROOT}/"):
        path = path[len(SITE_ROOT) :]
    return path or "/"


def literal(value: Any, level: int = 0) -> str:
    """Python source for a JSON value.

    A value that fits on its line stays on one line; longer ones put one
    item per line, as ``black`` would.

    :param value: A value decoded from JSON.
    :param level: Indentation level of the line the value starts on.
    :returns: The source.
    """
    inline = _inline(value)
    if len(INDENT * level) + len(inline) <= WIDTH - 8:
        return inline
    inner = INDENT * (level + 1)
    if isinstance(value, dict) and value:
        items = [
            f"{inner}{_inline(str(key))}: {literal(item, level + 1)},"
            for key, item in value.items()
        ]
        return "{\n" + "\n".join(items) + f"\n{INDENT * level}}}"
    if isinstance(value, list) and value:
        items = [f"{inner}{literal(item, level + 1)}," for item in value]
        return "[\n" + "\n".join(items) + f"\n{INDENT * level}]"
    return inline


def _inline(value: Any) -> str:
    """Python source for a JSON value, on one line.

    :param value: A value decoded from JSON.
    :returns: The source.
    """
    if isinstance(value, dict):
        items = ", ".join(f"{_inline(str(k))}: {_inline(v)}" for k, v in value.items())
        return "{" + items + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_inline(item) for item in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return repr(value)


def query_params(query: str) -> dict[str, Any]:
    """The parameters of a query string, with repeated keys as lists.

    plone-client writes a list as repeated keys, so this is its inverse.

    :param query: The query string.
    :returns: Parameters by name.
    """
    params: dict[str, Any] = {}
    for key, value in parse_qsl(query, keep_blank_values=True):
        if key not in params:
            params[key] = value
        elif isinstance(params[key], list):
            params[key].append(value)
        else:
            params[key] = [params[key], value]
    return params


def is_keyword_argument(name: str) -> bool:
    """Whether a query parameter can be passed as ``name=value``.

    :param name: Name of the parameter.
    :returns: ``True`` for a Python identifier that ``client.get`` does not
        use itself.
    """
    return name.isidentifier() and not keyword.iskeyword(name) and name != "ref"


def call(name: str, arguments: list[str]) -> str:
    """Python source of a call on ``client``.

    :param name: The method.
    :param arguments: Source of each argument.
    :returns: One line, or one argument per line when that is too long.
    """
    line = f"client.{name}({', '.join(arguments)})"
    if len(line) <= WIDTH and "\n" not in line:
        return line
    body = "\n".join(f"{INDENT}{argument}," for argument in arguments)
    return f"client.{name}(\n{body}\n)"


def keyword_arguments(values: dict[str, Any]) -> list[str]:
    """Source of keyword arguments.

    :param values: Values by name.
    :returns: ``name=value`` for each one.
    """
    return [f"{name}={literal(value, 1)}" for name, value in values.items()]


def raw_body(request: HTTPRequest) -> bytes:
    """The body of a request, byte for byte.

    ``HTTPRequest.data()`` joins the lines of a body that is not JSON with an
    extra newline, which breaks a ``multipart/form-data`` body.

    :param request: The parsed request.
    :returns: The body as it was recorded.
    """
    cursor = request.rfile.tell()
    body = request.rfile.read()
    request.rfile.seek(cursor)
    return body.strip()


def bytes_literal(body: bytes, level: int = 1) -> str:
    """Python source for a raw body, one line of the body per line.

    :param body: The body.
    :param level: Indentation level of the line the value starts on.
    :returns: A ``bytes`` literal, or several in parentheses.
    """
    lines = body.splitlines(keepends=True)
    if len(lines) < 2:
        return repr(body)
    inner = INDENT * (level + 1)
    parts = "\n".join(f"{inner}{line!r}" for line in lines)
    return f"(\n{parts}\n{INDENT * level})"


def build_plone_client_python(request: HTTPRequest) -> str:
    """The plone-client call that sends a recorded request.

    :param request: The request, as ``sphinxcontrib-httpexample`` parsed it.
    :returns: Python source.
    """
    method = request.command.upper()
    url = urlsplit(request.url())
    path = site_path(url.path)
    params = query_params(url.query)

    content_type = request.headers.get("Content-Type", "")
    is_json = content_type.split(";")[0].strip() == "application/json"
    headers: dict[str, str] = {}
    for name, value in request.headers.items():
        lower = name.lower()
        if lower in IMPLICIT_HEADERS:
            continue
        if lower == "accept" and value == "application/json":
            continue
        if lower == "content-type" and is_json:
            continue
        headers[name] = value

    data = request.data()
    has_raw_body = data is not None and not is_json

    if method in GENERIC and not has_raw_body and not headers:
        arguments = [_inline(path)]
        if method == "GET":
            if all(is_keyword_argument(name) for name in params):
                arguments += keyword_arguments(params)
            elif params:
                arguments.append(f"**{literal(params, 1)}")
            return call("get", arguments)
        if data is not None:
            arguments.append(literal(data, 1))
        if params:
            arguments.append(f"params={literal(params, 1)}")
        return call(method.lower(), arguments)

    arguments = [_inline(method), _inline(path)]
    extra: dict[str, Any] = {}
    if params:
        extra["params"] = params
    if headers:
        extra["headers"] = headers
    arguments += keyword_arguments(extra)
    if has_raw_body:
        arguments.append(f"content={bytes_literal(raw_body(request))}")
    elif data is not None:
        arguments.append(f"json={literal(data, 1)}")
    return call("request", arguments)
