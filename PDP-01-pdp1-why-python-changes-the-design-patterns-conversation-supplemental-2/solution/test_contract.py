import unittest
import main as lab

class Contract(unittest.TestCase):

    def test_function_and_whitespace(self):
        self.assertEqual(lab.title_case('  design patterns  '), '  Design Patterns  ')
        self.assertEqual(lab.title_case(''), '')
        with self.assertRaises(TypeError):
            lab.title_case(4)

    def test_closure_and_object_are_interchangeable(self):
        values = ['design patterns', '', 'already UPPER', '  spaced  ']
        expected = ['LOG: design patterns', 'LOG: ', 'LOG: already UPPER', 'LOG:   spaced  ']
        for formatter in [lab.make_prefix_formatter('LOG: '), lab.PrefixFormatter('LOG: ')]:
            self.assertEqual(lab.format_messages(values, formatter), expected)
        self.assertEqual(values, ['design patterns', '', 'already UPPER', '  spaced  '])

    def test_configuration_isolation(self):
        a = lab.make_prefix_formatter('A:')
        b = lab.make_prefix_formatter('B:')
        self.assertEqual([a('x'), b('x'), a('y')], ['A:x', 'B:x', 'A:y'])
        self.assertEqual(lab.PrefixFormatter('')('x'), 'x')

    def test_configuration_validation(self):
        for factory in [lab.make_prefix_formatter, lab.PrefixFormatter]:
            with self.assertRaises(TypeError):
                factory(None)

    def test_driver_order_empty_and_bad_returns(self):
        calls = []

        def recording(text):
            calls.append(text)
            return text.upper()
        self.assertEqual(lab.format_messages(iter(['b', 'a']), recording), ['B', 'A'])
        self.assertEqual(calls, ['b', 'a'])
        self.assertEqual(lab.format_messages([], recording), [])
        with self.assertRaises(TypeError):
            lab.format_messages(['ok', 2], recording)
        with self.assertRaises(TypeError):
            lab.format_messages(['ok'], lambda _: 2)
if __name__ == '__main__':
    unittest.main()
