import unittest
import main as lab

class Contract(unittest.TestCase):

    def test_named_rules(self):
        rules = lab.make_rulebook('LOG: ')
        self.assertEqual(list(rules), ['title', 'prefix', 'identity'])
        values = ['design patterns', '']
        self.assertEqual(lab.format_named(values, 'title', rules), ['Design Patterns', ''])
        self.assertEqual(lab.format_named(values, 'prefix', rules), ['LOG: design patterns', 'LOG: '])
        self.assertEqual(lab.format_named(values, 'identity', rules), values)

    def test_named_configuration_and_registry_isolation(self):
        a = lab.make_rulebook('A:')
        b = lab.make_rulebook('B:')
        a['extra'] = str.upper
        self.assertNotIn('extra', b)
        self.assertEqual(a['prefix']('x'), 'A:x')
        self.assertEqual(b['prefix']('x'), 'B:x')
        self.assertEqual(lab.make_rulebook('')['prefix']('x'), 'x')

    def test_custom_rule_needs_no_subclass(self):
        rules = {'reverse': lambda text: text[::-1]}
        self.assertEqual(lab.format_named(['abc', ''], 'reverse', rules), ['cba', ''])
        self.assertEqual(list(rules), ['reverse'])

    def test_missing_choice_fails_even_for_empty_input(self):
        rules = lab.make_rulebook('')
        with self.assertRaises(ValueError) as caught:
            lab.format_named([], 'missing', rules)
        self.assertIsInstance(caught.exception.__cause__, KeyError)
        self.assertEqual(list(rules), ['title', 'prefix', 'identity'])

    def test_bad_rule_inputs_and_returns(self):
        for action in [lambda: lab.select_formatter(None, {}), lambda: lab.select_formatter('bad', {'bad': 4}), lambda: lab.format_named([4], 'identity', lab.make_rulebook('')), lambda: lab.format_named(['ok'], 'bad', {'bad': lambda _: 4})]:
            with self.assertRaises(TypeError):
                action()
if __name__ == '__main__':
    unittest.main()
