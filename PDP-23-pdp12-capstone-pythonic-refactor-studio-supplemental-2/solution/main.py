"""Measure a flat module graph from syntax without executing its sources."""
import ast
import keyword
from collections.abc import Iterable, Mapping


def module_name(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("module names must be text")
    if not value.isidentifier() or keyword.iskeyword(value):
        raise ValueError("use flat Python module identifiers")
    return value


def dependency_map(sources: Mapping[str, str]) -> dict[str, tuple[str, ...]]:
    owned = dict(sources)
    for name, source in owned.items():
        module_name(name)
        if not isinstance(source, str):
            raise TypeError("module source must be text")
    result: dict[str, tuple[str, ...]] = {}
    for name in sorted(owned):
        tree = ast.parse(owned[name], filename=name + ".py")
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise ValueError("relative imports are outside this flat-module model")
                if node.module:
                    imports.add(node.module.split(".")[0])
        result[name] = tuple(sorted(imports & owned.keys()))
    return result


def affected_modules(dependencies: Mapping[str, Iterable[str]], changed: str) -> tuple[str, ...]:
    owned = {module_name(name): tuple(edges) for name, edges in dependencies.items()}
    for edges in owned.values():
        for edge in edges:
            module_name(edge)
            if edge not in owned:
                raise ValueError("every internal dependency needs a module entry")
    module_name(changed)
    if changed not in owned:
        raise KeyError(changed)
    affected = {changed}
    pending = [changed]
    while pending:
        target = pending.pop()
        for name, edges in owned.items():
            if target in edges and name not in affected:
                affected.add(name)
                pending.append(name)
    return tuple(sorted(affected))


def main() -> None:
    sources = {"app": "from model import Article\nfrom render import view",
               "model": "", "render": "from model import Article"}
    graph = dependency_map(sources)
    print("imports:", graph)
    print("affected by model:", affected_modules(graph, "model"))


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
