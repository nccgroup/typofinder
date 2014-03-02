from unittest import TestCase
from typogen import typogen


class TestTypogen(TestCase):
    def test_generate_missing_character_typos(self):
        result = typogen.generate_missing_character_typos("abc")
        self.assertListEqual(["ab", "ac", "bc"], sorted(result))

    def test_generate_duplicate_character_typos(self):
        result = typogen.generate_duplicate_character_typos("abc")
        self.assertListEqual(["aabc", "abbc", "abcc"], sorted(result))

    def test_generate_transposed_character_typos(self):
        result = typogen.generate_transposed_character_typos("abc")
        self.assertListEqual(["acb", "bac"], sorted(result))

    def test_generate_miskeyed_typos(self):
        result = typogen.generate_miskeyed_typos("abc", "gb")
        self.assertListEqual(['abd', 'abf', 'abv', 'abx', 'afc', 'agc', 'ahc', 'anc', 'avc', 'qbc', 'sbc', 'wbc', 'xbc', 'zbc'], sorted(result))

    def test_generate_miskeyed_sequence_typos(self):
        result = typogen.generate_miskeyed_sequence_typos("aabcc", "gb")
        self.assertListEqual(['aabdd', 'aabff', 'aabvv', 'aabxx', 'qqbcc', 'ssbcc', 'wwbcc', 'xxbcc', 'zzbcc'], sorted(result))
        result = typogen.generate_miskeyed_sequence_typos("aabccc", "gb")
        self.assertListEqual(['aabddd', 'aabfff', 'aabvvv', 'aabxxx', 'qqbccc', 'ssbccc', 'wwbccc', 'xxbccc', 'zzbccc'], sorted(result))
        result = typogen.generate_miskeyed_sequence_typos("abc", "gb")
        self.assertListEqual([], sorted(result))

    def test_generate_miskeyed_addition_typos(self):
        result = typogen.generate_miskeyed_addition_typos("abc", "gb")
        self.assertListEqual(sorted(['abcd', 'abcf', 'abcv', 'abcx', 'abfc', 'abgc', 'abhc', 'abnc', 'abvc', 'aqbc', 'asbc', 'awbc', 'axbc', 'azbc',
                              'abdc', 'abfc', 'abvc', 'abxc', 'afbc', 'agbc', 'ahbc', 'anbc', 'avbc', 'qabc', 'sabc', 'wabc', 'xabc', 'zabc']), sorted(result))