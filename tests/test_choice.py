import unittest

from asn1ate import parser
from asn1ate.sema import *
from tinyber.walker import Walker

from tinyber.py_nodes import PythonBackend as Backend
from tinyber import py_nodes as nodes

from tests.utils import generate, test_reload


class TestBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate("tests/test_choice.asn1", "gen_choice")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_choice1(self):
        test_reload()
        import tests.gen_choice_ber
        # Test length > 0x80
        s = bytearray(0x81)
        choice1 = tests.gen_choice_ber.Choice1(test1=5, str1=s)
        choice1.encode()


if __name__ == '__main__':
    unittest.main()
