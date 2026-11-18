"""State-dependent actions with one-shot commands and bounded, reversible history."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from typing import Protocol

LOCATIONS = {"camp": "camp", "exploring": "forest trail", "boss": "boss gate"}


def integer(value: object, label: str, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(label + " must be an integer")
    if value < minimum:
        raise ValueError(label + " is too small")
    return value


@dataclass(frozen=True)
class Snapshot:
    mode: str
    location: str
    energy: int

    def __post_init__(self) -> None:
        if self.mode not in LOCATIONS:
            raise ValueError("unknown quest mode")
        if not isinstance(self.location, str) or not self.location.strip():
            raise ValueError("location must be nonblank text")
        integer(self.energy, "energy")


@dataclass(frozen=True)
class Action:
    name: str
    amount: int = 1

    def __post_init__(self) -> None:
        if self.name not in {"move", "rest", "attack"}:
            raise ValueError("unknown action")
        integer(self.amount, "amount", 1)
        if self.name == "move" and self.amount != 1:
            raise ValueError("move amount must be one")


class InvalidAction(ValueError):
    """A well-formed action is unavailable in the current mode."""


class QuestState(Protocol):
    name: str
    def move(self, context: QuestContext) -> None: ...
    def attack(self, context: QuestContext, amount: int = 1) -> None: ...


def branch_move(context: QuestContext) -> None:
    if context.mode == "camp":
        context.transition(ExploringState(), LOCATIONS["exploring"])
    elif context.mode == "exploring":
        context.transition(BossState(), LOCATIONS["boss"])
    else:
        raise InvalidAction("already at the boss gate")


def branch_attack(context: QuestContext, amount: int) -> None:
    if context.mode == "boss":
        if context.energy < amount:
            raise InvalidAction("insufficient energy")
        context.energy -= amount


class CampState:
    name = "camp"
    def move(self, context: QuestContext) -> None:
        branch_move(context)
    def attack(self, context: QuestContext, amount: int = 1) -> None:
        branch_attack(context, amount)


class ExploringState(CampState):
    name = "exploring"


class BossState(CampState):
    name = "boss"


def state_named(name: str) -> QuestState:
    states: dict[str, Callable[[], QuestState]] = {
        "camp": CampState, "exploring": ExploringState, "boss": BossState}
    try:
        return states[name]()
    except KeyError as error:
        raise ValueError("unknown quest mode") from error


class QuestContext:
    def __init__(self, state: QuestState | None = None, location: str | None = None,
                 energy: int = 3, *, history_limit: int = 4) -> None:
        self.state = state if state is not None else CampState()
        self.location = LOCATIONS[self.state.name] if location is None else location
        self.energy = energy
        self._limit = integer(history_limit, "history_limit", 1)
        if self._limit > 1000:
            raise ValueError("history_limit exceeds 1000 entries")
        self._history: list[HistoryEntry] = []
        self._busy = False
        self.snapshot()

    @property
    def mode(self) -> str:
        return self.state.name

    @property
    def history_limit(self) -> int:
        return self._limit

    @property
    def history(self) -> tuple[HistoryEntry, ...]:
        return tuple(self._history)

    def snapshot(self) -> Snapshot:
        return Snapshot(self.mode, self.location, self.energy)

    def transition(self, state: QuestState, location: str) -> None:
        Snapshot(state.name, location, self.energy)
        self.state, self.location = state, location

    def _restore(self, value: Snapshot) -> None:
        self.state, self.location, self.energy = (
            state_named(value.mode), value.location, value.energy)


@dataclass(frozen=True)
class HistoryEntry:
    action: Action
    before: Snapshot
    after: Snapshot
    command: Command


class Command:
    def __init__(self, action: Action) -> None:
        if not isinstance(action, Action):
            raise TypeError("command requires an immutable Action")
        self._action = action
        self._status = "new"
        self._owner: QuestContext | None = None

    @property
    def action(self) -> Action:
        return self._action

    @property
    def status(self) -> str:
        return self._status

    def cancel(self) -> None:
        if self.status != "new":
            raise RuntimeError("only a new command can be cancelled")
        self._status = "cancelled"

    def perform(self, context: QuestContext) -> None:
        if self.action.name == "move":
            context.state.move(context)
        elif self.action.name == "attack":
            context.state.attack(context, self.action.amount)
        else:
            context.energy += self.action.amount

    def execute(self, context: QuestContext) -> None:
        if self.status != "new" or context._busy:
            raise RuntimeError("command is consumed or context is executing")
        before = context.snapshot()
        if context.history and before != context.history[-1].after:
            raise RuntimeError("quest changed outside command history")
        self._status, self._owner, context._busy = "running", context, True
        try:
            self.perform(context)
            after = context.snapshot()
        except BaseException:
            context._restore(before)
            self._status = "failed"
            raise
        else:
            context._history.append(HistoryEntry(self.action, before, after, self))
            del context._history[:-context.history_limit]
            self._status = "done"
        finally:
            context._busy = False

    def undo(self, context: QuestContext) -> None:
        if (context._busy or self.status != "done" or self._owner is not context
                or not context._history or context._history[-1].command is not self):
            raise RuntimeError("undo requires the latest retained command and its owner")
        entry = context._history[-1]
        if context.snapshot() != entry.after:
            raise RuntimeError("quest changed outside command history")
        context._restore(entry.before)
        context._history.pop()
        self._status = "undone"


class MoveCommand(Command):
    name = "move"
    def __init__(self) -> None:
        super().__init__(Action(self.name))


class RestCommand(Command):
    name = "rest"
    def __init__(self, amount: int = 1) -> None:
        super().__init__(Action(self.name, amount))


class AttackCommand(Command):
    name = "attack"
    def __init__(self, amount: int = 1) -> None:
        super().__init__(Action(self.name, amount))


def run_command(context: QuestContext, command: Command) -> None:
    command.execute(context)


def undo_last(context: QuestContext) -> bool:
    if context._busy:
        raise RuntimeError("quest is executing")
    if not context.history:
        return False
    context.history[-1].command.undo(context)
    return True


def move(context: QuestContext) -> None:
    run_command(context, MoveCommand())


def rest(context: QuestContext) -> None:
    run_command(context, RestCommand())


def attack(context: QuestContext) -> None:
    run_command(context, AttackCommand())


COMMANDS: dict[str, Callable[[QuestContext], None]] = {
    "move": move, "rest": rest, "attack": attack}


def export_actions(context: QuestContext) -> str:
    if context._busy:
        raise RuntimeError("quest is executing")
    entries = context.history
    initial = entries[0].before if entries else context.snapshot()
    expected = entries[-1].after if entries else initial
    if context.snapshot() != expected:
        raise RuntimeError("quest changed outside command history")
    if any(type(e.command).perform is not Command.perform for e in entries):
        raise ValueError("recording supports built-in action behavior only")
    text = json.dumps({"version": 1, "history_limit": context.history_limit,
        "initial": {"mode": initial.mode, "location": initial.location,
                    "energy": initial.energy},
        "actions": [{"name": e.action.name, "amount": e.action.amount} for e in entries]},
        sort_keys=True)
    if replay_actions(text).snapshot() != context.snapshot():
        raise ValueError("effects cannot be represented by the action recording")
    return text


def replay_actions(text: str) -> QuestContext:
    if not isinstance(text, str):
        raise TypeError("recording must be JSON text")
    if len(text) > 65536:
        raise ValueError("recording exceeds 65536 characters")
    data = json.loads(text)
    if not isinstance(data, dict) or set(data) != {"version", "history_limit", "initial", "actions"}:
        raise ValueError("invalid recording envelope")
    if type(data["version"]) is not int or data["version"] != 1:
        raise ValueError("unsupported recording version")
    raw = data["initial"]
    if not isinstance(raw, dict) or set(raw) != {"mode", "location", "energy"}:
        raise ValueError("invalid initial snapshot")
    initial = Snapshot(**raw)
    limit = integer(data["history_limit"], "history_limit", 1)
    values = data["actions"]
    if not isinstance(values, list) or len(values) > limit or len(values) > 1000:
        raise ValueError("invalid bounded actions")
    actions = []
    for value in values:
        if not isinstance(value, dict) or set(value) != {"name", "amount"}:
            raise ValueError("invalid action record")
        actions.append(Action(**value))
    result = QuestContext(state_named(initial.mode), initial.location,
                          initial.energy, history_limit=limit)
    for action in actions:
        run_command(result, Command(action))
    return result


def main() -> None:
    context = QuestContext()
    for name in ["move", "move", "attack", "rest"]:
        COMMANDS[name](context)
    undo_last(context)
    print(context.location, context.mode, context.energy)
    print("retained:", len(context.history))
    print("replay equal:", replay_actions(export_actions(context)).snapshot() == context.snapshot())


if __name__ == "__main__":
    main()
