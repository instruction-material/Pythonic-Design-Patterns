"""Learner contract: run after completing the two declared bodies."""
from dataclasses import FrozenInstanceError
import unittest
from main import MemorySender, Notice, deliver_notice, render_notice


class NoticeContract(unittest.TestCase):
    def test_render_and_value_boundaries(self):
        self.assertEqual(render_notice(Notice("build", "ready")), "[build] ready")
        self.assertEqual(render_notice(Notice("build", "")), "[build] ")
        self.assertEqual(render_notice(Notice(" café ", "  ready  ")),
                         "[ café ]   ready  ")
        for topic in ["", "  "]:
            with self.assertRaises(ValueError):
                Notice(topic, "ready")
        for topic, text in [(None, "ready"), ("build", 3)]:
            with self.assertRaises(TypeError):
                Notice(topic, text)

    def test_composition_and_exactly_once_delivery(self):
        class CustomSender:
            def __init__(self):
                self.sent = []
            def send(self, text):
                self.sent.append(text)
        sender = CustomSender()
        self.assertEqual(deliver_notice(Notice("a", "one"), sender), "[a] one")
        self.assertEqual(deliver_notice(Notice("b", ""), sender), "[b] ")
        self.assertEqual(sender.sent, ["[a] one", "[b] "])

    def test_independent_senders_and_frozen_value(self):
        first, second = MemorySender(), MemorySender()
        notice = Notice("build", "ready")
        deliver_notice(notice, first)
        self.assertEqual(first.messages, ["[build] ready"])
        self.assertEqual(second.messages, [])
        with self.assertRaises(FrozenInstanceError):
            notice.topic = "other"
        self.assertEqual(notice, Notice("build", "ready"))

    def test_malformed_runtime_collaborator_and_notice(self):
        class NotCallable:
            send = 7
        notice = Notice("build", "ready")
        for sender in [object(), NotCallable()]:
            with self.assertRaises(TypeError):
                deliver_notice(notice, sender)
        with self.assertRaises(TypeError):
            render_notice(object())
        with self.assertRaises(TypeError):
            deliver_notice(object(), MemorySender())

    def test_delivery_failure_propagates_without_retry(self):
        class FailingSender:
            def __init__(self):
                self.calls = 0
            def send(self, text):
                self.calls += 1
                raise LookupError("offline")
        sender = FailingSender()
        with self.assertRaisesRegex(LookupError, "^offline$"):
            deliver_notice(Notice("build", "ready"), sender)
        self.assertEqual(sender.calls, 1)


if __name__ == "__main__":
    unittest.main()
