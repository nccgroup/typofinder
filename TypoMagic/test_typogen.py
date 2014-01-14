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
