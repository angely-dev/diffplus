from .expected import configA_dict, configA_str
from .expected import configB_dict, configB_str
from .expected import diffmerge_dict, diffmerge_str, diffmerge_str_colored
from .expected import diffonly_dict, diffonly_str, diffonly_str_colored
from diffplus import IndentedConfig, IncrementalDiff
import unittest

configA = open("tests/configA.txt").read()
configB = open("tests/configB.txt").read()

configA = IndentedConfig(configA, comment_char="!", sanitize=False)
configB = IndentedConfig(configB, comment_char="!", sanitize=True)
configA.sanitize()


class TestDiffPlus(unittest.TestCase):
    def test_indented_config(self):
        self.assertRaises(ValueError, IndentedConfig, config="", indent_char="  ")
        self.assertRaises(ValueError, IndentedConfig, config="", comment_char="##")

        self.assertEqual(configA.to_dict(), configA_dict)
        self.assertEqual(configA.__str__(), configA_str)

        self.assertEqual(configB.to_dict(), configB_dict)
        self.assertEqual(configB.__str__(), configB_str)

    def test_incremental_diff(self):
        diffonly = IncrementalDiff(configA, configB, merge=False)
        self.assertEqual(diffonly.to_dict(), diffonly_dict)
        self.assertEqual(diffonly.__str__(), diffonly_str)

        diffmerge = IncrementalDiff(configA, configB, merge=True)
        self.assertEqual(diffmerge.to_dict(), diffmerge_dict)
        self.assertEqual(diffmerge.__str__(), diffmerge_str)

        diffonly.colored = True
        diffmerge.colored = True
        self.assertEqual(diffonly.__str__(), diffonly_str_colored)
        self.assertEqual(diffmerge.__str__(), diffmerge_str_colored)
