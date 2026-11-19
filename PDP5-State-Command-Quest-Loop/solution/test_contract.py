from dataclasses import FrozenInstanceError
import json
import subprocess
import sys
import unittest
from main import (Action, AttackCommand, BossState, COMMANDS, CampState, Command,
    InvalidAction, MoveCommand, QuestContext, RestCommand, Snapshot, export_actions,
    replay_actions, run_command, undo_last)


class QuestContracts(unittest.TestCase):
    def test_legacy_functions_and_state_transitions(self):
        ctx=QuestContext(); self.assertEqual(ctx.snapshot(),Snapshot("camp","camp",3))
        COMMANDS["move"](ctx); self.assertEqual(ctx.mode,"exploring")
        COMMANDS["move"](ctx); self.assertEqual((ctx.mode,ctx.location),("boss","boss gate"))
        before=ctx.snapshot()
        with self.assertRaises(InvalidAction): COMMANDS["move"](ctx)
        self.assertEqual(ctx.snapshot(),before); self.assertEqual(len(ctx.history),2)

    def test_attack_undo_restores_only_the_actual_effect(self):
        for state in [CampState(),BossState()]:
            ctx=QuestContext(state=state); before=ctx.snapshot()
            run_command(ctx,AttackCommand()); undo_last(ctx)
            self.assertEqual(ctx.snapshot(),before)
        ctx=QuestContext(state=BossState(),energy=0)
        with self.assertRaises(InvalidAction): run_command(ctx,AttackCommand())
        self.assertEqual((ctx.energy,ctx.history),(0,()))

    def test_lifo_empty_and_out_of_order_undo(self):
        ctx=QuestContext(); first,second=MoveCommand(),RestCommand(2)
        self.assertFalse(undo_last(ctx))
        run_command(ctx,first); run_command(ctx,second)
        with self.assertRaises(RuntimeError): first.undo(ctx)
        self.assertTrue(undo_last(ctx)); self.assertEqual(ctx.energy,3)
        self.assertTrue(undo_last(ctx)); self.assertEqual(ctx.mode,"camp")
        self.assertFalse(undo_last(ctx))

    def test_one_shot_success_failure_undo_and_cancellation(self):
        ctx=QuestContext(); command=RestCommand()
        run_command(ctx,command)
        with self.assertRaises(RuntimeError): run_command(ctx,command)
        undo_last(ctx)
        with self.assertRaises(RuntimeError): run_command(ctx,command)
        cancelled=RestCommand(); cancelled.cancel()
        with self.assertRaises(RuntimeError): run_command(ctx,cancelled)
        self.assertEqual(cancelled.status,"cancelled"); self.assertEqual(ctx.energy,3)
        failed=MoveCommand(); boss=QuestContext(state=BossState())
        with self.assertRaises(InvalidAction): run_command(boss,failed)
        self.assertEqual(failed.status,"failed")
        with self.assertRaises(RuntimeError): run_command(ctx,failed)

    def test_partial_failure_rolls_back_and_keeps_error_identity(self):
        error=LookupError("partial failure")
        class Broken(Command):
            def perform(self,ctx):
                ctx.energy+=9; ctx.transition(BossState(),"temporary"); raise error
        ctx=QuestContext(); before=ctx.snapshot(); command=Broken(Action("rest"))
        with self.assertRaises(LookupError) as caught: run_command(ctx,command)
        self.assertIs(caught.exception,error); self.assertEqual(ctx.snapshot(),before)
        self.assertEqual(ctx.history,()); self.assertEqual(command.status,"failed")
        run_command(ctx,RestCommand()); self.assertEqual(ctx.energy,4)

    def test_bounded_history_eviction_and_saved_initial_state(self):
        ctx=QuestContext(history_limit=2); commands=[RestCommand() for _ in range(3)]
        for c in commands: run_command(ctx,c)
        self.assertEqual([e.before.energy for e in ctx.history],[4,5])
        with self.assertRaises(RuntimeError): commands[0].undo(ctx)
        recording=export_actions(ctx); self.assertEqual(json.loads(recording)["initial"]["energy"],4)
        self.assertEqual(replay_actions(recording).snapshot(),ctx.snapshot())
        undo_last(ctx); undo_last(ctx); self.assertEqual(ctx.energy,4)
        self.assertFalse(undo_last(ctx))

    def test_action_capture_is_immutable_and_numeric_configuration_is_validated(self):
        action=Action("rest",3); command=Command(action)
        with self.assertRaises(FrozenInstanceError): action.amount=9
        ctx=QuestContext(); run_command(ctx,command); self.assertEqual(ctx.energy,6)
        for value in [True,1.5,"2"]:
            with self.assertRaises(TypeError): RestCommand(value)
            with self.assertRaises(TypeError): QuestContext(history_limit=value)
        for limit in [0,1001]:
            with self.assertRaises(ValueError): QuestContext(history_limit=limit)
        with self.assertRaises(ValueError): Action("move",2)
        with self.assertRaises(ValueError): Action("unknown")

    def test_replay_works_in_a_fresh_process_after_history_eviction(self):
        ctx=QuestContext(history_limit=2)
        for _ in range(5): run_command(ctx,RestCommand(2))
        text=export_actions(ctx)
        code="from main import replay_actions; import sys; c=replay_actions(sys.argv[1]); print(c.mode,c.location,c.energy,len(c.history))"
        result=subprocess.run([sys.executable,"-B","-c",code,text],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,"camp camp 13 2\n")

    def test_replay_rejects_malformed_and_unavailable_actions(self):
        base=json.loads(export_actions(QuestContext()))
        cases=[{},dict(base,version=True),dict(base,version=2),dict(base,history_limit=0),
               dict(base,initial={"mode":"unknown","location":"camp","energy":3}),
               dict(base,actions=[{"name":"rest","amount":True}]),
               dict(base,actions=[{"name":"move","amount":1}]*3)]
        for value in cases:
            with self.subTest(value=value),self.assertRaises((ValueError,TypeError)):
                replay_actions(json.dumps(value))
        with self.assertRaises(ValueError): replay_actions("x"*65537)

    def test_external_mutation_prevents_silent_undo_recording_and_execution(self):
        ctx=QuestContext(); run_command(ctx,RestCommand()); ctx.energy+=7
        with self.assertRaises(RuntimeError): undo_last(ctx)
        with self.assertRaises(RuntimeError): export_actions(ctx)
        command=RestCommand()
        with self.assertRaises(RuntimeError): run_command(ctx,command)
        self.assertEqual(command.status,"new")

    def test_reentrant_execution_is_rejected_and_rolled_back(self):
        class Nested(Command):
            def perform(self,ctx):
                ctx.energy+=8; run_command(ctx,RestCommand())
        ctx=QuestContext()
        with self.assertRaises(RuntimeError): run_command(ctx,Nested(Action("rest")))
        self.assertEqual(ctx.snapshot(),Snapshot("camp","camp",3)); self.assertEqual(ctx.history,())

    def test_histories_are_owned_and_custom_effects_cannot_be_exported_as_builtin_actions(self):
        a,b=QuestContext(),QuestContext(); command=RestCommand(); run_command(a,command)
        with self.assertRaises(RuntimeError): command.undo(b)
        self.assertEqual((a.energy,b.energy),(4,3)); self.assertEqual(b.history,())
        class Custom(Command):
            def perform(self,ctx): ctx.energy+=5
        custom=QuestContext(); run_command(custom,Custom(Action("rest")))
        with self.assertRaises(ValueError): export_actions(custom)
        undo_last(custom); self.assertEqual(custom.energy,3)


if __name__=="__main__": unittest.main()
