"""Custom sphinxcontrib-httpexample builder for @plone/client."""

from urllib.parse import parse_qs
from urllib.parse import urlparse
import re

from sphinx.util import logging
from sphinxcontrib.httpexample import HTTPRequest


logger = logging.getLogger(__name__)


def is_valid_js_identifier(key):
    return re.match(r"^[_a-zA-Z][_a-zA-Z0-9]*$", key)


def python_to_js_literal(value, indent=0):
    indent_str = " " * indent
    next_indent_str = " " * (indent + 1)

    if isinstance(value, dict):
        lines = ["{"]
        for k, v in value.items():
            key = k if is_valid_js_identifier(k) else f"'{k}'"
            js_val = python_to_js_literal(v, indent + 1)
            lines.append(f"{next_indent_str}{key}: {js_val},")
        lines.append(f"{indent_str}}}")
        return "\n".join(lines)

    if isinstance(value, list):
        if not value:
            return "[]"
        items = [f"{python_to_js_literal(item, indent + 1)}," for item in value]
        return (
            "[\n"
            + "\n".join(f"{next_indent_str}{item}" for item in items)
            + f"\n{indent_str}]"
        )

    if isinstance(value, str):
        return f"'{value}'"

    if isinstance(value, bool):
        return "true" if value else "false"

    if value is None:
        return "null"

    return str(value)


def content_path(url):
    """Return path relative to the portal root."""
    parts = url.path.strip("/").split("/", 1)
    if len(parts) == 1:
        return "/"
    return f"/{parts[1]}"


def aliases_item_path(path):
    """Return the content path for an /@aliases request.

    Root ``/@aliases`` maps to an empty string so
    ``${path}/@aliases`` becomes ``/@aliases``.
    """
    if path in ("/", "/@aliases"):
        return ""
    if path.endswith("/@aliases"):
        return path[: -len("/@aliases")] or ""
    return None


def aliases_call(request: HTTPRequest):
    url = urlparse(request.url())
    path = content_path(url)
    qs = parse_qs(url.query)
    data = request.data() or {}
    item_path = aliases_item_path(path)

    if item_path is None:
        return None

    # Query / CSV / other Accept types are not supported by @plone/client yet.
    if qs or (
        request.headers.get("Accept", "application/json") != "application/json"
        and request.command == "GET"
    ):
        return None
    content_type = request.headers.get("Content-Type", "")
    if content_type and not content_type.startswith("application/json"):
        return None

    if request.command == "GET" and item_path == "":
        return "const { data, status } = await cli.getAllAliases();\n"

    if request.command == "GET":
        payload = {"path": item_path}
        return (
            f"const {{ data, status }} = await cli.getAliases("
            f"{python_to_js_literal(payload)});\n"
        )

    if request.command == "POST" and item_path == "":
        payload = {"data": data}
        return f"await cli.createAliases({python_to_js_literal(payload)});\n"

    if request.command == "POST":
        payload = {"path": item_path, "data": data}
        return f"await cli.createAlias({python_to_js_literal(payload)});\n"

    if request.command == "DELETE":
        payload = {"path": item_path, "data": data}
        return f"await cli.deleteAliases({python_to_js_literal(payload)});\n"

    return None


def get_content(request: HTTPRequest):
    url = urlparse(request.url())
    path = content_path(url)
    qs = parse_qs(url.query)
    payload = {
        "path": path,
    }
    if qs.get("expand"):
        payload["expand"] = qs.get("expand", [])[0].split(",")
    return f"""\
const {{ data, status }} = await cli.getContent({python_to_js_literal(payload)});
"""


def patch_content(request: HTTPRequest):
    url = urlparse(request.url())
    path = content_path(url)
    payload = {
        "path": path,
        "data": request.data(),
    }
    return f"""\
await cli.updateContent({python_to_js_literal(payload)});
"""


def post_content(request: HTTPRequest):
    url = urlparse(request.url())
    path = content_path(url)
    payload = {
        "path": path,
        "data": request.data(),
    }
    return f"""\
await cli.createContent({python_to_js_literal(payload)});
"""


def delete_content(request: HTTPRequest):
    url = urlparse(request.url())
    path = content_path(url)
    payload = {
        "path": path,
    }
    return f"""\
await cli.deleteContent({python_to_js_literal(payload)});
"""


def build_plone_client_command(request: HTTPRequest) -> str:
    url = urlparse(request.url())
    portal_path = url.path.split("/")[1]
    output = f"""\
import PloneClient from '@plone/client';

const cli = PloneClient.initialize({{apiPath: '{url.scheme}://{url.netloc}/{portal_path}'}});

"""
    auth = request.auth()
    if auth[-1]:
        username, password = auth[-1].split(":")
        output += f"""\
await cli.login({{username: '{username}', password: '{password}'}});

"""

    aliases = aliases_call(request)
    if aliases is not None:
        return output + aliases

    path = content_path(url)
    if "/@" in path:
        logger.warning(
            "No @plone/client mapping for %s %s",
            request.command,
            path,
        )
        return output + (
            f"// No @plone/client mapping for {request.command} {path} yet.\n"
        )

    if request.command == "GET":
        return output + get_content(request)
    if request.command == "PATCH":
        return output + patch_content(request)
    if request.command == "POST":
        return output + post_content(request)
    if request.command == "DELETE":
        return output + delete_content(request)

    logger.warning(
        "No @plone/client mapping for %s %s",
        request.command,
        path,
    )
    return output + (
        f"// No @plone/client mapping for {request.command} {path} yet.\n"
    )
