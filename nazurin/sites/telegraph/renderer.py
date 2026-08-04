from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any
from urllib.parse import urljoin, urlsplit

SAFE_LINK_SCHEMES = {"http", "https", "mailto"}
SAFE_MEDIA_SCHEMES = {"http", "https"}

DIRECT_TAGS = {
    "aside",
    "blockquote",
    "code",
    "em",
    "figcaption",
    "figure",
    "h3",
    "h4",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "u",
    "ul",
}
TAG_ALIASES = {"b": "strong", "i": "em"}
VOID_TAGS = {"br", "hr"}


@dataclass(frozen=True)
class ImageReference:
    occurrence: int
    url: str | None


def safe_url(value: object, base_url: str, schemes: set[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    resolved = urljoin(base_url, value.strip())
    try:
        parsed = urlsplit(resolved)
        port = parsed.port
    except ValueError:
        return None
    scheme = parsed.scheme.lower()
    if scheme == "mailto":
        return resolved if scheme in schemes and bool(parsed.path) else None
    if (
        scheme not in schemes
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
    ):
        return None
    return resolved


def collect_image_references(nodes: list[Any], base_url: str) -> list[ImageReference]:
    """Collect image nodes in document order."""
    references: list[ImageReference] = []
    occurrence = 0

    def visit(node: object):
        nonlocal occurrence
        if not isinstance(node, dict):
            return
        tag = node.get("tag")
        attrs = node.get("attrs") if isinstance(node.get("attrs"), dict) else {}
        if tag == "img":
            occurrence += 1
            url = safe_url(attrs.get("src"), base_url, SAFE_MEDIA_SCHEMES)
            references.append(
                ImageReference(
                    occurrence=occurrence,
                    url=url,
                ),
            )
        children = node.get("children")
        if isinstance(children, list):
            for child in children:
                visit(child)

    for node in nodes:
        visit(node)
    return references


class TelegraphRenderer:
    def __init__(
        self,
        page: dict,
        source_url: str,
        image_paths: dict[int, str] | None = None,
    ):
        self.page = page
        self.source_url = source_url
        self.image_paths = image_paths or {}
        self._image_occurrence = 0

    def render(self) -> str:
        self._image_occurrence = 0
        title = escape(self.page["title"], quote=False)
        author = self._render_author()
        source = self._render_source()
        content = self._render_nodes(self.page["content"])
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      color: #222;
      font-family: system-ui, sans-serif;
      line-height: 1.65;
      margin: 2rem auto;
      max-width: 46rem;
      padding: 0 1rem;
    }}
    img, video {{ height: auto; max-width: 100%; }}
    figure {{ margin: 1.5rem 0; }}
    figcaption {{ color: #666; font-size: 0.9rem; }}
    blockquote {{
      border-left: 0.25rem solid #ccc;
      margin-left: 0;
      padding-left: 1rem;
    }}
    pre {{ background: #f5f5f5; overflow-x: auto; padding: 1rem; }}
    .source, .embed {{ color: #666; }}
  </style>
</head>
<body>
  <article>
    <h1>{title}</h1>
    {author}
    {content}
    {source}
  </article>
</body>
</html>
"""

    def _render_author(self) -> str:
        author_name = self.page.get("author_name")
        if not isinstance(author_name, str) or not author_name:
            return ""
        name = escape(author_name, quote=False)
        author_url = safe_url(
            self.page.get("author_url"),
            self.source_url,
            SAFE_LINK_SCHEMES,
        )
        if author_url:
            href = escape(author_url, quote=True)
            return (
                f'<p class="author">By <a href="{href}" '
                f'rel="noopener noreferrer">{name}</a></p>'
            )
        return f'<p class="author">By {name}</p>'

    def _render_source(self) -> str:
        source_url = safe_url(self.source_url, self.source_url, SAFE_MEDIA_SCHEMES)
        if not source_url:
            return ""
        href = escape(source_url, quote=True)
        return (
            f'<p class="source"><a href="{href}" rel="noopener noreferrer">'
            "Original page</a></p>"
        )

    def _render_nodes(self, nodes: list[Any]) -> str:
        return "".join(self._render_node(node) for node in nodes)

    def _render_node(self, node: object) -> str:  # noqa: PLR0911
        if isinstance(node, str):
            return escape(node, quote=False)
        if not isinstance(node, dict):
            return ""

        tag = node.get("tag")
        children = node.get("children")
        rendered_children = (
            self._render_nodes(children) if isinstance(children, list) else ""
        )

        tag = TAG_ALIASES.get(tag, tag)
        match tag:
            case _ if tag in DIRECT_TAGS:
                return f"<{tag}>{rendered_children}</{tag}>"
            case _ if tag in VOID_TAGS:
                return f"<{tag}/>"
            case "a":
                return self._render_anchor(node, rendered_children)
            case "img":
                return self._render_image(node)
            case "iframe" | "video":
                return self._render_embed(node, tag, rendered_children)
            case _:
                return rendered_children

    def _attrs(self, node: dict) -> dict:
        attrs = node.get("attrs")
        return attrs if isinstance(attrs, dict) else {}

    def _render_anchor(self, node: dict, children: str) -> str:
        href = safe_url(
            self._attrs(node).get("href"),
            self.source_url,
            SAFE_LINK_SCHEMES,
        )
        if not href:
            return children
        label = children or escape(href, quote=False)
        escaped_href = escape(href, quote=True)
        return f'<a href="{escaped_href}" rel="noopener noreferrer">{label}</a>'

    def _render_image(self, node: dict) -> str:
        self._image_occurrence += 1
        local_path = self.image_paths.get(self._image_occurrence)
        if local_path:
            return f'<img src="{escape(local_path, quote=True)}" alt="">'

        source = safe_url(
            self._attrs(node).get("src"),
            self.source_url,
            SAFE_MEDIA_SCHEMES,
        )
        if not source:
            return ""
        href = escape(source, quote=True)
        return (
            f'<a class="image-link" href="{href}" rel="noopener noreferrer">Image</a>'
        )

    def _render_embed(self, node: dict, tag: str, children: str) -> str:
        source = safe_url(
            self._attrs(node).get("src"),
            self.source_url,
            SAFE_MEDIA_SCHEMES,
        )
        link = ""
        if source:
            href = escape(source, quote=True)
            label = "Video" if tag == "video" else "Embedded content"
            link = f'<a href="{href}" rel="noopener noreferrer">{label}</a>'
        content = link + children
        return f'<span class="embed">{content}</span>' if content else ""
