"""Markdown Renderer - converts Python data structures to Markdown with YAML frontmatter."""

from datetime import date
from datetime import datetime
from plone.restapi.interfaces import IRenderer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import json
import re


@implementer(IRenderer)
@adapter(Interface)
class MarkdownRenderer:
    """Render data as GitHub Flavored Markdown with YAML frontmatter."""

    content_type = "text/markdown"

    # Fields to exclude from frontmatter
    EXCLUDED_FROM_FRONTMATTER = {"blocks", "blocks_layout"}

    # Fields that contain the main content body
    BODY_FIELDS = {"text", "description"}

    def __init__(self, request):
        self.request = request

    def __call__(self, data):
        """Convert Python data structure to Markdown with YAML frontmatter."""
        if not isinstance(data, dict):
            # For non-dict data (lists, etc.), just return JSON representation
            return json.dumps(data, indent=2)

        # Extract metadata and body
        frontmatter = {}
        body_parts = []

        for key, value in data.items():
            if key in self.EXCLUDED_FROM_FRONTMATTER:
                # Handle blocks separately
                if key == "blocks":
                    body_parts.extend(
                        self._render_blocks(value, data.get("blocks_layout", {}))
                    )
            elif key in self.BODY_FIELDS:
                # These go into the body, not frontmatter
                if key == "text" and isinstance(value, dict):
                    # RichText field structure
                    body_parts.append(self._render_richtext(value))
                elif value:
                    body_parts.append(str(value))
            else:
                # Everything else goes to frontmatter
                frontmatter[key] = value

        # Build the document
        parts = []

        # Add YAML frontmatter
        if frontmatter:
            parts.append("---")
            parts.append(self._render_yaml(frontmatter))
            parts.append("---")
            parts.append("")

        # Add title as H1 if present
        if "title" in data and data["title"]:
            parts.append(f"# {data['title']}")
            parts.append("")

        # Add body content
        if body_parts:
            parts.extend(body_parts)

        return "\n".join(parts)

    def _render_yaml(self, data, indent=0):
        """Convert a Python dict to YAML format."""
        lines = []
        prefix = "  " * indent

        for key, value in sorted(data.items()):
            if value is None:
                lines.append(f"{prefix}{key}:")
            elif isinstance(value, bool):
                lines.append(f"{prefix}{key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines.append(f"{prefix}{key}: {value}")
            elif isinstance(value, str):
                # Escape special characters and quote if necessary
                if "\n" in value or ":" in value or value.startswith(("@", "-", "[")):
                    # Multi-line or special string
                    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'{prefix}{key}: "{escaped}"')
                else:
                    lines.append(f"{prefix}{key}: {value}")
            elif isinstance(value, (datetime, date)):
                lines.append(f"{prefix}{key}: {value.isoformat()}")
            elif isinstance(value, (list, tuple)):
                if not value:
                    lines.append(f"{prefix}{key}: []")
                else:
                    lines.append(f"{prefix}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"{prefix}  -")
                            lines.append(self._render_yaml(item, indent + 2))
                        else:
                            lines.append(f"{prefix}  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._render_yaml(value, indent + 1))
            else:
                # Fallback to string representation
                lines.append(f"{prefix}{key}: {str(value)}")

        return "\n".join(lines)

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

    def _render_blocks(self, blocks, blocks_layout):
        """Convert Volto blocks to Markdown.

        Simple text blocks are converted to Markdown, complex blocks are
        embedded as JSON with four backticks.
        """
        if not blocks:
            return []

        result = []

        # Get the order of blocks from blocks_layout
        items_order = (
            blocks_layout.get("items", []) if isinstance(blocks_layout, dict) else []
        )
        if not items_order:
            items_order = sorted(blocks.keys())

        for block_id in items_order:
            if block_id not in blocks:
                continue

            block = blocks[block_id]
            block_type = block.get("@type", "unknown")

            # Try to render as simple Markdown
            markdown = self._render_block_as_markdown(block, block_type)

            if markdown:
                result.append(markdown)
            else:
                # Complex block - embed as JSON
                result.append("````json")
                result.append(json.dumps(block, indent=2))
                result.append("````")

            result.append("")  # Empty line between blocks

        return result

    def _render_block_as_markdown(self, block, block_type):
        """Try to render a block as simple Markdown.

        Returns None if the block is too complex and should be embedded as JSON.
        """
        # Text blocks (simple paragraph)
        if block_type == "text":
            text = block.get("text", "")
            if isinstance(text, dict):
                # Slate format
                return self._render_slate_to_markdown(text)
            elif isinstance(text, str):
                return self._html_to_markdown(text)

        # Title blocks
        elif block_type == "title":
            return f"# {block.get('title', '')}"

        # Description blocks
        elif block_type == "description":
            return block.get("description", "")

        # Image blocks
        elif block_type == "image":
            url = block.get("url", "")
            alt = block.get("alt", "")
            if url:
                return f"![{alt}]({url})"

        # Return None for complex blocks
        return None

    def _render_slate_to_markdown(self, slate_data):
        """Convert Slate format to Markdown.

        Slate is the rich text editor format used by Volto.
        """
        if not slate_data:
            return ""

        # Simple implementation - just extract text
        # A full implementation would need to handle formatting, links, etc.
        def extract_text(node):
            if isinstance(node, str):
                return node
            if isinstance(node, dict):
                text = node.get("text", "")
                if text:
                    return text
                children = node.get("children", [])
                return "".join(extract_text(child) for child in children)
            if isinstance(node, list):
                return "".join(extract_text(item) for item in node)
            return ""

        return extract_text(slate_data)
