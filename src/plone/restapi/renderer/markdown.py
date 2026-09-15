"""Markdown Renderer - converts Python data structures to Markdown with YAML frontmatter."""

from plone.restapi.interfaces import IConvertBlockToMarkdown
from plone.restapi.interfaces import IRenderer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import json
import re
import yaml

EXCLUDED_FROM_FRONTMATTER = {"blocks", "blocks_layout"}
BODY_FIELDS = {"text", "description"}


@implementer(IRenderer)
@adapter(Interface, Interface)
class MarkdownRenderer:
    """Render data as GitHub Flavored Markdown with YAML frontmatter."""

    content_type = "text/markdown"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, data):
        """Convert Python data structure to Markdown with YAML frontmatter."""

        if not isinstance(data, dict):
            return json.dumps(data, indent=2)

        frontmatter = {}
        body_parts = []

        for key, value in data.items():
            if key in EXCLUDED_FROM_FRONTMATTER:
                if key == "blocks":
                    body_parts.extend(
                        self._render_blocks(value, data.get("blocks_layout", []))
                    )
            elif key in BODY_FIELDS:
                # These go into the body, not frontmatter
                if key == "text" and isinstance(value, dict):
                    # RichText field structure
                    body_parts.append(self._render_richtext(value))
                elif value:
                    body_parts.append(str(value))
            else:
                frontmatter[key] = value

        parts = []

        if frontmatter:
            parts.append("---")
            parts.append(
                yaml.dump(
                    frontmatter, default_flow_style=False, allow_unicode=True
                ).rstrip("\n")
            )
            parts.append("---")
            parts.append("")

        # Add title as H1 if present
        # TODO: this makes content objects with the blocks behavior have two titles
        # because of the title block converter
        if "title" in data and data["title"]:
            parts.append(f"# {data['title']}")
            parts.append("")

        if body_parts:
            parts.extend(body_parts)

        return "\n".join(parts)

    def _html_to_markdown(self, html):
        """Convert HTML to GitHub Flavored Markdown.

        This is a basic implementation. For production use, consider using
        a library like 'markdownify' or 'html2text'.
        """
        if not html:
            return ""

        text = html

        # Convert headings
        text = re.sub(
            r"<h1[^>]*>(.*?)</h1>", r"# \1", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h2[^>]*>(.*?)</h2>", r"## \1", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h3[^>]*>(.*?)</h3>", r"### \1", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h4[^>]*>(.*?)</h4>", r"#### \1", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h5[^>]*>(.*?)</h5>", r"##### \1", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h6[^>]*>(.*?)</h6>", r"###### \1", text, flags=re.IGNORECASE | re.DOTALL
        )

        # Convert bold and italic
        text = re.sub(
            r"<strong[^>]*>(.*?)</strong>",
            r"**\1**",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(
            r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.IGNORECASE | re.DOTALL
        )

        # Convert links
        text = re.sub(
            r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            r"[\2](\1)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Convert images
        text = re.sub(
            r'<img[^>]*src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>',
            r"![\2](\1)",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*src=["\']([^"\']+)["\'][^>]*>',
            r"![\1](\2)",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r"![](\1)",
            text,
            flags=re.IGNORECASE,
        )

        # Convert lists
        text = re.sub(r"<ul[^>]*>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"</ul>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<ol[^>]*>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"</ol>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(
            r"<li[^>]*>(.*?)</li>", r"- \1", text, flags=re.IGNORECASE | re.DOTALL
        )

        # Convert paragraphs
        text = re.sub(
            r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.IGNORECASE | re.DOTALL
        )

        # Convert line breaks
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

        # Convert code
        text = re.sub(
            r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<pre[^>]*>(.*?)</pre>",
            r"```\n\1\n```",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    def _render_richtext(self, richtext_data):
        """Convert a RichText field to Markdown."""
        if not isinstance(richtext_data, dict):
            return str(richtext_data)

        content = richtext_data.get("data", "")
        content_type = richtext_data.get("content-type", "text/plain")

        if content_type == "text/html":
            return self._html_to_markdown(content)
        elif content_type == "text/plain":
            return content
        else:
            # Unknown content type, return as-is
            return content

    def _render_blocks(self, blocks, blocks_layout):
        """Convert Volto blocks to Markdown.

        Simple text blocks are converted to Markdown, complex blocks are
        embedded as JSON with four backticks.
        """
        if not blocks:
            return []

        result = []

        blocks_order = (
            blocks_layout.get("items", []) if isinstance(blocks_layout, dict) else []
        )
        if not blocks_order:
            blocks_order = sorted(blocks.keys())

        for block_id in blocks_order:
            if block_id not in blocks:
                continue

            block = blocks[block_id]
            block_type = block.get("@type", "unknown")

            adapter = queryMultiAdapter(
                (self.context, self.request), IConvertBlockToMarkdown, name=block_type
            )

            if adapter:
                result.append(adapter(block))
            else:
                result.append("````json")
                result.append(json.dumps(block, indent=2))
                result.append("````")

            result.append("")

        return result
