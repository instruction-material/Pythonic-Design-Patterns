"""Acquire a chosen resource set and release it in reverse order."""
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

def require_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("resource name must be a string")
    if not name.strip():
        raise ValueError("resource name must not be blank")
    return name

@contextmanager
def managed_resource(name: str, trace: list[str], *,
                     fail_acquire: bool = False, suppress: bool = False) -> Iterator[str]:
    require_name(name)
    trace.append("acquire:" + name)
    if fail_acquire:
        trace.append("failed:" + name)
        raise OSError("acquisition failed: " + name)
    try:
        yield name
    except ValueError:
        if not suppress:
            raise
        trace.append("suppressed:" + name)
    finally:
        trace.append("release:" + name)

def run_resources(names: list[str], trace: list[str], *,
                  fail_at: str | None = None, fail_body: bool = False,
                  suppress_at: str | None = None) -> str:
    selected = tuple(names)
    for name in selected:
        require_name(name)
    outcome = "suppressed"
    with ExitStack() as stack:
        for name in selected:
            stack.enter_context(managed_resource(
                name, trace, fail_acquire=name == fail_at,
                suppress=name == suppress_at))
        trace.append("body")
        if fail_body:
            raise ValueError("body failed")
        outcome = "complete"
    return outcome

def main() -> None:
    trace: list[str] = []
    try:
        result = run_resources(["profile", "billing"], trace)
        print("result:", result)
        print("trace:", trace)
    except NotImplementedError:
        print("PDP6 starter unfinished: Complete managed_resource and run_resources.")

if __name__ == "__main__":
    main()
