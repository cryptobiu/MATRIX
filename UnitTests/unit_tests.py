import unittest
from ExperimentExecute import pre_process


class MyTestCase(unittest.TestCase):
    def test_something(self):
        p = pre_process.PreProcess()
        val = p.create_circuits()
        self.assertEqual(val, 1)


if __name__ == '__main__':
    unittest.main()
