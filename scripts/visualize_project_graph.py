"""Create a browser-viewable architecture graph without starting the RAG app.

The exporter reads Python source with ``ast`` and writes a self-contained HTML
file containing:

* a module dependency graph for ``src``;
* the active LangGraph request path, including the cache branch;
* a small legend and node statistics.

It intentionally does not import application modules, open databases, load
models, contact the web, or call the local LLM.
"""

from __future__ import annotations

import argparse
import ast
import html
from pathlib import Path


WORKFLOW_EDGES = [
    ("START", "preprocess", "request"),
    ("preprocess", "route", "request"),
    ("route", "cache", "request"),
    ("cache", "END", "cache hit"),
    ("cache", "retrieve", "cache miss"),
    ("retrieve", "context", "evidence"),
    ("context", "generate", "prompt"),
    ("generate", "memory_write", "answer"),
    ("memory_write", "cache_write", "history"),
    ("cache_write", "END", "stored"),
]


def module_name(path: Path, root: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imported_modules(path: Path, root: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()

    imports: set[str] = set()
    current = module_name(path, root).split(".")[:-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(
                alias.name.removeprefix("src.")
                for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = current[: len(current) - node.level + 1]
                if node.module:
                    base.extend(node.module.split("."))
                imports.add(".".join(base).removeprefix("src."))
            elif node.module:
                imports.add(node.module.removeprefix("src."))

    return imports


def dependency_edges(root: Path) -> tuple[set[str], list[tuple[str, str, str]]]:
    source_root = root / "src"
    modules = {
        module_name(path, source_root)
        for path in source_root.rglob("*.py")
    }
    edges: list[tuple[str, str, str]] = []

    for path in source_root.rglob("*.py"):
        source = module_name(path, source_root)
        for imported in imported_modules(path, source_root):
            target = imported
            while target and target not in modules:
                target = target.rpartition(".")[0]
            if target and target != source:
                edges.append((source, target, "imports"))

    return modules, sorted(set(edges))


def mermaid_graph(root: Path) -> tuple[str, int, int]:
    modules, edges = dependency_edges(root)
    lines = [
        "flowchart LR",
        "  subgraph Request[\"Active request workflow\"]",
    ]
    workflow_nodes = {source for source, _, _ in WORKFLOW_EDGES}
    workflow_nodes.update(target for _, target, _ in WORKFLOW_EDGES)

    for node in sorted(workflow_nodes):
        safe = node.replace("-", "_")
        lines.append(f'    {safe}["{node}"]')
    for source, target, label in WORKFLOW_EDGES:
        lines.append(f'    {source.replace("-", "_")} -->|{label}| {target.replace("-", "_")}')
    lines.append("  end")
    lines.append('  classDef workflow fill:#0f766e,stroke:#99f6e4,color:#fff;')
    lines.append("  class " + ",".join(sorted(node.replace("-", "_") for node in workflow_nodes)) + " workflow;")

    lines.append('  subgraph Modules["Python module dependencies"]')
    for module in sorted(modules):
        node = "m_" + module.replace(".", "_")
        label = module.replace('"', "'")
        lines.append(f'    {node}["{label}"]')
    for source, target, label in edges:
        lines.append(
            f"    m_{source.replace('.', '_')} -.->|{label}| m_{target.replace('.', '_')}"
        )
    lines.append("  end")
    lines.append('  classDef module fill:#1e3a8a,stroke:#93c5fd,color:#fff;')
    if modules:
        lines.append("  class " + ",".join("m_" + module.replace(".", "_") for module in sorted(modules)) + " module;")

    return "\n".join(lines), len(modules), len(edges)


def write_html(root: Path, output: Path) -> None:
    graph, module_count, edge_count = mermaid_graph(root)
    escaped_graph = html.escape(graph)
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hybrid Agentic RAG architecture</title>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true, theme: "dark", securityLevel: "strict" }});
  </script>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; background: #07111f; color: #e2e8f0; font: 15px system-ui, sans-serif; }}
    header {{ padding: 24px 32px; background: linear-gradient(120deg, #0f766e, #1e3a8a); }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    .meta {{ opacity: .85; }}
    main {{ padding: 24px; overflow: auto; }}
    .mermaid {{ min-width: 1100px; }}
    code {{ color: #99f6e4; }}
  </style>
</head>
<body>
  <header>
    <h1>Hybrid Agentic RAG architecture</h1>
    <div class="meta">{module_count} Python modules · {edge_count} import edges · static source analysis only</div>
  </header>
  <main>
    <p>Solid teal nodes are the active request path. Blue nodes are source modules. Dashed edges are imports.</p>
    <pre class="mermaid">{escaped_graph}</pre>
  </main>
</body>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (defaults to the repository containing this script).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/project_graph.html"),
        help="HTML output path.",
    )
    args = parser.parse_args()
    write_html(args.root.resolve(), args.output.resolve())
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
