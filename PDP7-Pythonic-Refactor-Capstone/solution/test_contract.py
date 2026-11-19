"""Public behavior and collaborator contracts for both complete programs."""
import copy
from dataclasses import FrozenInstanceError
import json
import unittest
from unittest.mock import patch
from typing import Any
import baseline_original as baseline
import main as lab


def outcome(function: Any, rows: Any, kind: str, uppercase: bool) -> object:
    module = baseline if function is baseline.run_workflow else lab
    with patch.object(module, "ARTICLES", copy.deepcopy(rows)):
        try:
            return ("returned", function(kind, uppercase))
        except Exception as error:
            return ("raised", type(error), error.args)


class Contract(unittest.TestCase):
    def test_01_legacy_characterization_matrix(self):
        cases = [[], baseline.ARTICLES, [baseline.ARTICLES[0]] * 2,
                 [{"title": " A ", "kind": " BLOG ", "body": " B "}],
                 [{"title": " A ", "kind": "other", "body": " B "}],
                 [{}], [{"kind": "news"}],
                 [{"title": None, "kind": "blog", "body": " B "}],
                 [{"title": " A ", "kind": [], "body": " B "}]]
        for rows in cases:
            for kind in ("all", "blog", "news", "missing"):
                for uppercase in (False, True):
                    with self.subTest(rows=rows, kind=kind, uppercase=uppercase):
                        self.assertEqual(outcome(lab.run_workflow, rows, kind, uppercase),
                                         outcome(baseline.run_workflow, rows, kind, uppercase))

    def test_02_normal_output_and_owned_input(self):
        rows = copy.deepcopy(baseline.ARTICLES)
        before = copy.deepcopy(rows)
        writes = []
        text = lab.run_application(lab.Config(), lambda: rows, writes.append)
        self.assertEqual(text, "[BLOG] hello world: python patterns\n[NEWS] system update: adapters and facades")
        self.assertEqual(writes, [text])
        self.assertEqual(rows, before)

    def test_03_filter_case_and_duplicates(self):
        rows = [baseline.ARTICLES[0], baseline.ARTICLES[0], baseline.ARTICLES[1]]
        text = lab.run_application(lab.Config("blog", True), lambda: rows, lambda _: None)
        self.assertEqual(text, "[BLOG] HELLO WORLD: PYTHON PATTERNS\n" * 1 + "[BLOG] HELLO WORLD: PYTHON PATTERNS")

    def test_04_padded_kind_and_field_access_priority(self):
        row = {"title": " A ", "body": " B ", "kind": " BLOG "}
        self.assertEqual(lab.run_application(lab.Config(), lambda: [row], lambda _: None),
                         "[OTHER] a: b")
        for kind, missing in [("all", "title"), ("blog", "kind")]:
            with self.assertRaises(KeyError) as error:
                lab.run_application(lab.Config(kind), lambda: [{}], lambda _: None)
            self.assertEqual(error.exception.args, (missing,))
        self.assertEqual(lab.run_application(lab.Config("blog"), lambda: [{"kind": "news"}], lambda _: None), "")

    def test_05_config_is_explicit_frozen_and_validated(self):
        config = lab.Config()
        with self.assertRaises(FrozenInstanceError): config.output = "json"
        for kwargs, error in [({"uppercase": 1}, TypeError), ({"kind_filter": None}, TypeError),
                              ({"output": " text"}, ValueError), ({"output": ""}, ValueError)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(error): lab.Config(**kwargs)

    def test_06_read_and_write_once_including_empty(self):
        events = []
        def read(): events.append("read"); return iter(())
        result = lab.run_application(lab.Config(), read, lambda text: events.append(("write", text)))
        self.assertEqual(result, "")
        self.assertEqual(events, ["read", ("write", "")])

    def test_07_json_and_provider_replacement(self):
        rows = [baseline.ARTICLES[0]]
        text = lab.run_application(lab.Config(output="json"), lambda: rows, lambda _: None)
        self.assertEqual(json.loads(text), [{"title": "hello world", "kind": "blog", "body": "python patterns"}])
        self.assertEqual(lab.run_application(lab.Config(), lambda: rows, lambda _: None,
                                             {"text": lambda articles: articles[0].title}), "hello world")

    def test_08_reader_error_identity_and_no_write(self):
        failure = OSError("source")
        writes = []
        def read(): raise failure
        with self.assertRaises(OSError) as error:
            lab.run_application(lab.Config(), read, writes.append)
        self.assertIs(error.exception, failure)
        self.assertEqual(writes, [])

    def test_09_prepare_entire_document_before_write(self):
        writes = []
        with self.assertRaises(KeyError):
            lab.run_application(lab.Config(), lambda: [baseline.ARTICLES[0], {}], writes.append)
        self.assertEqual(writes, [])

    def test_10_iterator_failure_before_write(self):
        writes = []
        failure = RuntimeError("iteration")
        def read():
            yield baseline.ARTICLES[0]
            raise failure
        with self.assertRaises(RuntimeError) as error:
            lab.run_application(lab.Config(), read, writes.append)
        self.assertIs(error.exception, failure)
        self.assertEqual(writes, [])

    def test_11_renderer_failure_identity_and_result_type(self):
        writes = []
        failure = LookupError("renderer")
        def render(articles): raise failure
        with self.assertRaises(LookupError) as error:
            lab.run_application(lab.Config(), lambda: [], writes.append, {"text": render})
        self.assertIs(error.exception, failure)
        with self.assertRaises(TypeError):
            lab.run_application(lab.Config(), lambda: [], writes.append, {"text": lambda _: None})
        self.assertEqual(writes, [])

    def test_12_writer_failure_preserves_visible_effect(self):
        writes = []
        failure = OSError("sink")
        def write(text): writes.append(text); raise failure
        with self.assertRaises(OSError) as error:
            lab.run_application(lab.Config(), lambda: [], write)
        self.assertIs(error.exception, failure)
        self.assertEqual(writes, [""])

    def test_13_capture_registry_before_reader_and_own_records(self):
        row = dict(baseline.ARTICLES[0])
        providers = {"text": lambda articles: articles[0].title}
        def read():
            providers["text"] = lambda articles: "changed"
            return [row]
        def write(text): row["title"] = "changed"
        self.assertEqual(lab.run_application(lab.Config(), read, write, providers), "hello world")

    def test_14_invalid_setup_has_no_io(self):
        events = []
        def read(): events.append("read"); return []
        for config, providers, error in [(lab.Config(output="missing"), None, KeyError),
            (lab.Config(), {" text": lambda _: ""}, ValueError),
            (lab.Config(), {"text": None}, TypeError), (None, None, TypeError)]:
            with self.subTest(config=config), self.assertRaises(error):
                lab.run_application(config, read, events.append, providers)
        with self.assertRaises(TypeError): lab.run_application(lab.Config(), read, None)
        self.assertEqual(events, [])

    def test_15_provider_receives_immutable_values_and_order(self):
        seen = []
        def render(articles):
            self.assertIsInstance(articles, tuple)
            with self.assertRaises(FrozenInstanceError): articles[0].title = "changed"
            seen.extend(item.kind for item in articles)
            return "ok"
        lab.run_application(lab.Config(), lambda: baseline.ARTICLES * 2, lambda _: None, {"text": render})
        self.assertEqual(seen, ["blog", "news", "blog", "news"])


if __name__ == "__main__": unittest.main()
