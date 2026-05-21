from plone.restapi.interfaces import IConvertBlockToMarkdown
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

NEWLINE = "\n"


@implementer(IConvertBlockToMarkdown)
@adapter(Interface, Interface)
class SlateSerializer:
    """"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_data):
        return "\n\n".join(
            [self._slate_to_markdown(node) for node in block_data.get("value", [])]
        )

    def _slate_to_markdown(self, slate_data):
        """Convert Slate format to Markdown.

        Slate is the rich text editor format used by Volto.
        """
        if not slate_data:
            return ""

        def extract_text(
            node: dict, depth: int = 0, index: int = 0, parent: str = ""
        ) -> str:
            count = 0
            children = ""

            if "children" in node:
                child_parts = []
                for child in node["children"]:
                    if isinstance(child, dict) and child.get("type"):
                        count += 1
                        child_parts.append(
                            extract_text(child, depth + 1, count, node.get("type", ""))
                        )
                    else:
                        child_parts.append(child.get("text", ""))
                children = "".join(child_parts)

            node_type = node.get("type", "") if isinstance(node, dict) else ""

            match node_type:
                case "p":
                    return f"{children}\n"
                case "blockquote":
                    return f"> {children}\n"
                case "h1":
                    return f"# {children}\n"
                case "h2":
                    return f"## {children}\n"
                case "h3":
                    return f"### {children}\n"
                case "h4":
                    return f"#### {children}\n"
                case "h5":
                    return f"##### {children}\n"
                case "h6":
                    return f"###### {children}\n"
                case "hr":
                    return "---\n"
                case "strong":
                    return f"**{children}**"
                case "em":
                    return f"*{children}*"
                case "del":
                    return f"~~{children}~~"
                case "sub":
                    return f"~{children}~"
                case "sup":
                    return f"^{children}^"
                case "link":
                    url = node.get("data", {}).get("url", "") if "data" in node else ""
                    return f"[{children}]({url})"
                case "li":
                    indent = "    " * (depth - 1)
                    if parent == "ol":
                        return f"{indent}{index}. {children}\n"
                    return f"{indent}- {children}\n"
                case "ul" | "ol":
                    return f"{children}{NEWLINE if depth == 0 else ''}"
                case _:
                    return children

        return extract_text(slate_data)
