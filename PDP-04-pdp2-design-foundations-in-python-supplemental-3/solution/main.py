"""Own mutable record state and make independent transport snapshots."""
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TypedDict


def require_name(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("name must be a string")
    if not value.strip():
        raise ValueError("name must contain a non-space character")
    return value


def require_tag(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("tag must be a string")
    if not value.strip():
        raise ValueError("tag must contain a non-space character")
    return value


@dataclass
class TaskRecord:
    name: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_task(self)


class TaskSnapshot(TypedDict):
    name: str
    tags: list[str]


def validate_task(task: TaskRecord) -> None:
    if not isinstance(task, TaskRecord):
        raise TypeError("task must be a TaskRecord")
    require_name(task.name)
    if not isinstance(task.tags, list):
        raise TypeError("task tags must be a list")
    for tag in task.tags:
        require_tag(tag)


def new_task(name: str, tags: Iterable[str] = ()) -> TaskRecord:
    """Create an owned list, preserving tag values, order and duplicates."""
    if isinstance(tags, (str, bytes)):
        raise TypeError("tags must be an iterable of tag strings")
    return TaskRecord(name, list(tags))


def snapshot_task(task: TaskRecord) -> TaskSnapshot:
    """Validate the current state and return an independent dictionary."""
    validate_task(task)
    return {"name": task.name, "tags": list(task.tags)}


def main() -> None:
    try:
        first = new_task("plan", ["new"])
        second = new_task("other")
        snapshot = snapshot_task(first)
        first.tags.append("ready")
        print("first:", snapshot_task(first))
        print("second:", snapshot_task(second))
        print("snapshot:", snapshot)
    except NotImplementedError as error:
        print("PDP2 starter unfinished:", error)


if __name__ == "__main__":
    main()
