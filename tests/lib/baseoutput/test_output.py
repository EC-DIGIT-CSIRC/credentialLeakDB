import unittest

from lib.baseoutput.output import BaseOutput

class TestBaseOutput(unittest.TestCase):
    def test_process(self):
        to = BaseOutput()
        assert to.process("test_outputfile.txt")
