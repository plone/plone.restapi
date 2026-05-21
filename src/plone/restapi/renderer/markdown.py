"""Markdown Renderer - converts Python data structures to Markdown with YAML frontmatter."""

from plone.restapi.interfaces import IConvertBlockToMarkdown
from plone.restapi.interfaces import IRenderer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import json
import yaml

EXCLUDED_FROM_FRONTMATTER = {"blocks", "blocks_layout"}


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

        if body_parts:
            parts.extend(body_parts)

        return "\n".join(parts)

    def _render_blocks(self, blocks: dict, blocks_layout: list) -> list[str]:
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
