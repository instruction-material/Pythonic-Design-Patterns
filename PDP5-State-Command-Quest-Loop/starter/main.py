from dataclasses import dataclass, field


@dataclass
class QuestContext:
	location: str = "camp"
	energy: int = 3
	mode: str = "camp"
	history: list[str] = field(default_factory=list)


def move(context: QuestContext) -> None:
	if context.mode == "camp":
		context.mode = "exploring"
		context.location = "forest trail"
		context.history.append("move")
	elif context.mode == "exploring":
		context.mode = "boss"
		context.location = "boss gate"
		context.history.append("move")


def rest(context: QuestContext) -> None:
	context.energy += 1
	context.history.append("rest")


def attack(context: QuestContext) -> None:
	if context.mode == "boss" and context.energy > 0:
		context.energy -= 1
		context.history.append("attack")


COMMANDS = {
	"move": move,
	"rest": rest,
	"attack": attack,
}


def main() -> None:
	context = QuestContext()
	for command_name in ["move", "move", "attack", "rest"]:
		COMMANDS[command_name](context)
	print(context)


if __name__ == "__main__":
	main()
