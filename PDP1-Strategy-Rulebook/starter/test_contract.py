import math
import unittest
from main import LineItem, RULES, build_rulebook, build_sample_cart, checkout_total, register_rule, subtotal


class PricingContract(unittest.TestCase):
    def test_published_sample_and_legacy_two_argument_call(self):
        cart = build_sample_cart()
        self.assertEqual([checkout_total(cart, name) for name in ["standard", "loyalty", "bulk"]], [49.5, 44.55, 41.5])
        self.assertEqual(subtotal(iter(cart)), 49.5)

    def test_empty_quantity_threshold_and_floor(self):
        self.assertEqual([checkout_total([], name) for name in RULES], [0, 0, 0])
        self.assertEqual(checkout_total([LineItem("item", 2.0, 5)], "bulk"), 10)
        self.assertEqual(checkout_total([LineItem("item", 2.0, 6)], "bulk"), 4)
        self.assertEqual(checkout_total([LineItem("free", 0.0, 6)], "bulk"), 0)
        self.assertEqual(checkout_total([LineItem("item", 9.0, 0)], "standard"), 0)

    def test_registry_isolation_duplicate_and_unknown(self):
        first, second = build_rulebook(), build_rulebook()
        register_rule(first, "free", lambda cart: 0.0)
        self.assertNotIn("free", second)
        with self.assertRaises(ValueError): register_rule(first, "free", lambda cart: 1.0)
        with self.assertRaises(KeyError): checkout_total([], "missing", second)
        with self.assertRaises(ValueError): register_rule(first, " ", lambda cart: 0.0)

    def test_call_once_list_ownership_and_failure(self):
        seen = []
        cart = [LineItem("item", 2.0)]
        def selected(copy):
            seen.append(len(copy))
            copy.clear()
            return 1.0
        self.assertEqual(checkout_total(cart, "chosen", {"chosen": selected}), 1)
        self.assertEqual(len(cart), 1)
        self.assertEqual(seen, [1])
        def fail(copy):
            seen.append("fail")
            raise LookupError("stop")
        with self.assertRaisesRegex(LookupError, "stop"):
            checkout_total(cart, "bad", {"bad": fail})
        self.assertEqual(seen, [1, "fail"])

    def test_line_item_validation(self):
        for value in [-1.0, math.inf, math.nan]:
            with self.assertRaises(ValueError): LineItem("item", value)
        for value in [True, "1"]:
            with self.assertRaises(TypeError): LineItem("item", value)
        with self.assertRaises(ValueError): LineItem(" ", 1)
        with self.assertRaises(TypeError): LineItem("item", 1, True)
        with self.assertRaises(ValueError): LineItem("item", 1, -1)
        with self.assertRaises(TypeError): checkout_total([object()], "standard")

    def test_result_validation_and_final_rounding(self):
        cart = [LineItem("item", 1)]
        self.assertEqual(checkout_total(cart, "round", {"round": lambda items: 1.234}), 1.23)
        for value in [-1.0, math.inf, math.nan]:
            with self.assertRaises(ValueError): checkout_total(cart, "bad", {"bad": lambda items: value})
        for value in [True, "1"]:
            with self.assertRaises(TypeError): checkout_total(cart, "bad", {"bad": lambda items: value})

    def test_configured_callables_keep_configuration_separate(self):
        # This public extension is implementable in either source form.
        def discount(fraction):
            return lambda items: subtotal(items) * (1 - fraction)
        self.assertEqual(checkout_total([LineItem("item", 10)], "a", {"a": discount(0.2)}), 8)
        self.assertEqual(checkout_total([LineItem("item", 10)], "b", {"b": discount(0.5)}), 5)


if __name__ == "__main__": unittest.main()
