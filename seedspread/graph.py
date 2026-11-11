"""A lightweight, language-level code graph built with Python's `ast`.

Nodes are files and the symbols they define (classes, functions, methods).
Edges:
  contains   file  -> symbol, class -> method          (structure)
  imports    file  -> file                             (resolved module imports)
  references symbol/file -> symbol                     (name-resolved calls / attribute uses)

Name resolution is deliberately approximate (no type inference): a reference to
`foo` links to every definition named `foo`, with weight split 1/k across the k
candidates. This keeps construction fast (seconds for Django) and dependency-free.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Symbol:
    id: str            # "path::Class.method"
    name: str          # "method"
    qualname: str      # "Class.method"
    path: str
    kind: str          # "class" | "function" | "method"
    signature: str
    line: int


@dataclass
class CodeGraph:
    files: dict[str, str]
    symbols: dict[str, Symbol] = field(default_factory=dict)
    by_name: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    edges: dict[str, dict[str, float]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))
    file_symbols: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    module_to_file: dict[str, str] = field(default_factory=dict)
    parse_failures: int = 0

    def add_edge(self, a: str, b: str, w: float = 1.0) -> None:
        if a != b:
            self.edges[a][b] += w

    @property
    def nodes(self) -> list[str]:
        return list(self.files) + list(self.symbols)


def module_name(path: str) -> str:
    mod = path[:-3].replace("/", ".")
    for prefix in ("src.", "lib."):
        if mod.startswith(prefix):
            mod = mod[len(prefix):]
    return mod[: -len(".__init__")] if mod.endswith(".__init__") else mod


def _signature(node: ast.AST) -> str:
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(b) for b in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    args = ast.unparse(node.args)
    if len(args) > 80:
        args = args[:77] + "..."
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args})"


class _Collector(ast.NodeVisitor):
    def __init__(self, g: CodeGraph, path: str):
        self.g, self.path, self.stack = g, path, []
        self.refs: list[tuple[str, str]] = []      # (from_node, name)
        self.imports: list[tuple[str | None, int, list[str]]] = []

    def _owner(self) -> str:
        return self.stack[-1] if self.stack else self.path

    def _define(self, node, kind):
        parent = self.g.symbols.get(self.stack[-1]) if self.stack else None
        qual = f"{parent.qualname}.{node.name}" if parent else node.name
        if parent and parent.kind != "class":       # nested helper: keep, attribute to parent
            qual = f"{parent.qualname}.<locals>.{node.name}"
        sid = f"{self.path}::{qual}"
        if kind == "function" and parent and parent.kind == "class":
            kind = "method"
        self.g.symbols[sid] = Symbol(sid, node.name, qual, self.path, kind, _signature(node), node.lineno)
        self.g.by_name[node.name].append(sid)
        self.g.file_symbols[self.path].append(sid)
        self.g.add_edge(self._owner(), sid, 1.0)    # contains
        self.g.add_edge(sid, self._owner(), 1.0)    # contained-in (lets PPR flow back up)
        for d in getattr(node, "decorator_list", []):
            self.visit(d)
        self.stack.append(sid)
        for child in node.body:
            self.visit(child)
        if not isinstance(node, ast.ClassDef):
            for d in node.args.defaults + node.args.kw_defaults:
                if d is not None:
                    self.visit(d)
        else:
            for b in node.bases:
                self.visit(b)
        self.stack.pop()

    def visit_ClassDef(self, node):
        self._define(node, "class")

    def visit_FunctionDef(self, node):
        self._define(node, "function")

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Name(self, node):
        self.refs.append((self._owner(), node.id))

    def visit_Attribute(self, node):
        self.refs.append((self._owner(), node.attr))
        self.generic_visit(node)

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append((a.name, 0, []))

    def visit_ImportFrom(self, node):
        self.imports.append((node.module, node.level, [a.name for a in node.names]))


def _resolve_import(g: CodeGraph, path: str, module: str | None, level: int, names: list[str]) -> list[str]:
    if level:
        base = module_name(path).split(".")
        is_pkg = path.endswith("__init__.py")
        base = base[: len(base) - level + (1 if is_pkg else 0)]
        module = ".".join(base + ([module] if module else []))
    if not module:
        return []
    hits = []
    for cand in [f"{module}.{n}" for n in names] + [module]:
        parts = cand.split(".")
        while parts:                                  # longest known prefix
            f = g.module_to_file.get(".".join(parts))
            if f:
                hits.append(f)
                break
            parts.pop()
    return hits


def build_graph(files: dict[str, str], max_bytes: int = 400_000) -> CodeGraph:
    g = CodeGraph(files=files)
    for p in files:
        g.module_to_file[module_name(p)] = p
    collectors = []
    for path, src in files.items():
        if len(src) > max_bytes:
            continue
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError, RecursionError):
            g.parse_failures += 1
            continue
        c = _Collector(g, path)
        for stmt in tree.body:
            c.visit(stmt)
        collectors.append(c)
    for c in collectors:
        for module, level, names in c.imports:
            for f in _resolve_import(g, c.path, module, level, names):
                g.add_edge(c.path, f, 1.0)
        seen = set()
        for owner, name in c.refs:
            if (owner, name) in seen:
                continue
            seen.add((owner, name))
            targets = g.by_name.get(name)
            if targets and len(targets) <= 50:       # ultra-common names carry no signal
                w = 1.0 / len(targets)
                for t in targets:
                    g.add_edge(owner, t, w)
    return g
