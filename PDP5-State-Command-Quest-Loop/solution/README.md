# State and Command Quest Loop

Python 3.14. Refactor mode dispatch from branch_move/branch_attack into CampState, ExploringState and BossState while preserving the public contracts and exact default output. The starter is a complete working baseline. Preserve QuestContext, Snapshot, immutable Action, Command and its Move/Rest/Attack variants, run_command, undo_last, legacy move/rest/attack/COMMANDS, export_actions and replay_actions.

QuestContext starts at camp with energy 3 and retains four history entries by default; history_limit is 1..1000. Move advances camp -> exploring -> boss; moving at boss raises InvalidAction. Attack outside boss is a recorded no-op. Boss attack consumes amount energy, and insufficient energy fails without a history entry. Rest adds its positive amount in every state. Numeric amounts exclude bool. State and location remain separate snapshot fields.

Command.action is immutable. A command is one-shot: success, failure, cancellation or undo consumes it; retry uses a fresh command. cancel() applies to a new command before execution. execute() snapshots local quest data, rejects reentrancy and restores local data on failure before propagating the same exception. Only successful actions enter history, including successful no-ops. Custom perform() implementations may change local quest data, but external effects cannot be rolled back. Custom command behavior cannot be exported as a built-in action recording.

Undo restores the exact before snapshot of the newest retained command and returns True. Empty undo returns False. Evicted, foreign, repeated or out-of-order undo is rejected. Editing quest data outside the recorded action stream causes undo, export and further execution to reject an inconsistent history. The history view is an immutable tuple.

Export is version-1 JSON containing the earliest retained before snapshot, history_limit and retained action name/amount pairs. This allows replay after old entries have been evicted. A fresh process replays built-in local quest actions with fresh command objects, without the original object identities. It reconstructs the retained window rather than an unlimited lifetime log. Invalid envelope keys, modes, versions, actions and unavailable transitions fail. Recordings are limited to 65536 characters and at most 1000 actions. Files, payments, network requests and custom side effects are outside this replay contract.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. The 12 public behavioral groups pass in both roles before refactoring. Development pins can be installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.

Default output:

```text
boss gate boss 2
retained: 3
replay equal: True
```

## Separate optional comparison client

Save this complete client next to main.py after making an independent attempt. It changes the history window or external schema/transform rather than repeating the core refactor.

```python
from main import QuestContext, RestCommand, export_actions, replay_actions, run_command, undo_last

context = QuestContext(history_limit=2)
for _ in range(3):
    run_command(context, RestCommand())
print("retained:", len(context.history))
replayed = replay_actions(export_actions(context))
print("replayed:", replayed.mode, replayed.energy)
undo_last(replayed)
undo_last(replayed)
print("undo floor:", replayed.energy)
print("empty:", undo_last(replayed))
```

Expected client output:

```text
retained: 2
replayed: camp 6
undo floor: 4
empty: False
```
