from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class QuestState(Protocol):
	name: str

	def move(self, context: QuestContext) -> None: ...

	def attack(self, context: QuestContext) -> None: ...


@dataclass
class QuestContext:
	state: QuestState
	location: str = "camp"
	energy: int = 3
	history: list[Command] = field(default_factory=list)

	def transition(self, state: QuestState, location: str) -> None:
		self.state = state
		self.location = location


class CampState:
	name = "camp"

	def move(self, context: QuestContext) -> None:
		context.transition(ExploringState(), "forest trail")

	def attack(self, context: QuestContext) -> None:
		print("No enemy at camp.")


class ExploringState:
	name = "exploring"

	def move(self, context: QuestContext) -> None:
		context.transition(BossState(), "boss gate")

	def attack(self, context: QuestContext) -> None:
		print("Save your energy for the boss.")


class BossState:
	name = "boss"

	def move(self, context: QuestContext) -> None:
		print("You are already at the boss gate.")

	def attack(self, context: QuestContext) -> None:
		if context.energy > 0:
			context.energy -= 1


class Command(Protocol):
	name: str

	def execute(self, context: QuestContext) -> None: ...

	def undo(self, context: QuestContext) -> None: ...


class MoveCommand:
	name = "move"

	def __init__(self) -> None:
		self.previous_state_name = ""
		self.previous_location = ""

	def execute(self, context: QuestContext) -> None:
		self.previous_state_name = context.state.name
		self.previous_location = context.location
		context.state.move(context)

	def undo(self, context: QuestContext) -> None:
		states = {
			"camp": CampState(),
			"exploring": ExploringState(),
			"boss": BossState(),
		}
		context.transition(states[self.previous_state_name], self.previous_location)


class RestCommand:
	name = "rest"

	def execute(self, context: QuestContext) -> None:
		context.energy += 1

	def undo(self, context: QuestContext) -> None:
		context.energy -= 1


class AttackCommand:
	name = "attack"

	def execute(self, context: QuestContext) -> None:
		context.state.attack(context)

	def undo(self, context: QuestContext) -> None:
		context.energy += 1


def run_command(context: QuestContext, command: Command) -> None:
	command.execute(context)
	context.history.append(command)


def undo_last(context: QuestContext) -> None:
	command = context.history.pop()
	command.undo(context)


def main() -> None:
	context = QuestContext(state=CampState())
	run_command(context, MoveCommand())
	run_command(context, MoveCommand())
	run_command(context, AttackCommand())
	run_command(context, RestCommand())
	undo_last(context)
	print(context.location, context.state.name, context.energy)


if __name__ == "__main__":
	main()
