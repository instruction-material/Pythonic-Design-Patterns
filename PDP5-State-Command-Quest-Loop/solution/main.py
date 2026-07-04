from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

#################
#   CONSTANTS   #
#################

CAMP_STATE_NAME = "camp"
EXPLORING_STATE_NAME = "exploring"
BOSS_STATE_NAME = "boss"
MOVE_COMMAND_NAME = "move"
REST_COMMAND_NAME = "rest"
ATTACK_COMMAND_NAME = "attack"
STARTING_LOCATION = CAMP_STATE_NAME
FOREST_LOCATION = "forest trail"
BOSS_LOCATION = "boss gate"
INITIAL_ENERGY = 3
MINIMUM_ATTACK_ENERGY = 0
ENERGY_STEP = 1
NO_ENEMY_MESSAGE = "No enemy at camp."
SAVE_ENERGY_MESSAGE = "Save your energy for the boss."
BOSS_GATE_MESSAGE = "You are already at the boss gate."


#############
#   TYPES   #
#############


# Define the interface shared by all quest states
class QuestState(Protocol):
    """Define actions supported by every quest state"""

    name: str

    def move(self, context: QuestContext) -> None:
        """Handle a move command in this state"""
        ...

    def attack(self, context: QuestContext) -> None:
        """Handle an attack command in this state"""
        ...


# Store the mutable quest state for the command loop
@dataclass
class QuestContext:
    """Track the current state, location, energy, and history"""

    state: QuestState
    location: str = STARTING_LOCATION
    energy: int = INITIAL_ENERGY
    history: list[Command] = field(default_factory=list)

    def transition(self, state: QuestState, location: str) -> None:
        """Move the quest context into a new state and location"""
        self.state = state
        self.location = location


# Represent the starting camp state
class CampState:
    """Handle quest actions while the player is at camp"""

    name = CAMP_STATE_NAME

    def move(self, context: QuestContext) -> None:
        """Move from camp to the forest trail"""
        context.transition(ExploringState(), FOREST_LOCATION)

    def attack(self, context: QuestContext) -> None:
        """Report that there is no camp enemy"""
        print(NO_ENEMY_MESSAGE)


# Represent the exploration state before the boss
class ExploringState:
    """Handle quest actions while the player explores"""

    name = EXPLORING_STATE_NAME

    def move(self, context: QuestContext) -> None:
        """Move from exploration to the boss gate"""
        context.transition(BossState(), BOSS_LOCATION)

    def attack(self, context: QuestContext) -> None:
        """Report that the player should save energy"""
        print(SAVE_ENERGY_MESSAGE)


# Represent the boss encounter state
class BossState:
    """Handle quest actions at the boss gate"""

    name = BOSS_STATE_NAME

    def move(self, context: QuestContext) -> None:
        """Report that movement is not needed at the boss gate"""
        print(BOSS_GATE_MESSAGE)

    def attack(self, context: QuestContext) -> None:
        """Spend energy when attacking the boss"""
        # Spend energy only when the player still has energy available
        if context.energy > MINIMUM_ATTACK_ENERGY:
            context.energy -= ENERGY_STEP


# Define the interface shared by undoable commands
class Command(Protocol):
    """Define command execution and undo behavior"""

    name: str

    def execute(self, context: QuestContext) -> None:
        """Apply this command to the quest context"""
        ...

    def undo(self, context: QuestContext) -> None:
        """Reverse this command on the quest context"""
        ...


# Move the quest forward while remembering the prior state
class MoveCommand:
    """Move the player and support undoing the movement"""

    name = MOVE_COMMAND_NAME

    def __init__(self) -> None:
        """Initialize empty previous-state storage"""
        self.previous_state_name = ""
        self.previous_location = ""

    def execute(self, context: QuestContext) -> None:
        """Run the move action for the current state"""
        self.previous_state_name = context.state.name
        self.previous_location = context.location
        context.state.move(context)

    def undo(self, context: QuestContext) -> None:
        """Restore the state and location from before the move"""
        states: dict[str, QuestState] = {
            CAMP_STATE_NAME: CampState(),
            EXPLORING_STATE_NAME: ExploringState(),
            BOSS_STATE_NAME: BossState(),
        }
        context.transition(states[self.previous_state_name], self.previous_location)


# Restore energy while supporting undo
class RestCommand:
    """Add energy and support undoing that rest"""

    name = REST_COMMAND_NAME

    def execute(self, context: QuestContext) -> None:
        """Add one energy point"""
        context.energy += ENERGY_STEP

    def undo(self, context: QuestContext) -> None:
        """Remove the energy point added by rest"""
        context.energy -= ENERGY_STEP


# Attack through the current state while supporting undo
class AttackCommand:
    """Attack in the current state and support undoing the attack"""

    name = ATTACK_COMMAND_NAME

    def execute(self, context: QuestContext) -> None:
        """Run the attack action for the current state"""
        context.state.attack(context)

    def undo(self, context: QuestContext) -> None:
        """Restore the energy spent by an attack"""
        context.energy += ENERGY_STEP


#################
#   FUNCTIONS   #
#################


def run_command(context: QuestContext, command: Command) -> None:
    """Execute a command and remember it for undo"""
    command.execute(context)
    context.history.append(command)


def undo_last(context: QuestContext) -> None:
    """Undo the most recent command in the history"""
    command = context.history.pop()
    command.undo(context)


def main() -> None:
    """Run a sample state and command sequence"""
    context = QuestContext(state=CampState())
    run_command(context, MoveCommand())
    run_command(context, MoveCommand())
    run_command(context, AttackCommand())
    run_command(context, RestCommand())
    undo_last(context)
    print(context.location, context.state.name, context.energy)


if __name__ == "__main__":
    main()
