import unittest
from app.util.matcher import match


class MatchTest(unittest.TestCase):

    def test_char_typo(self):
        cmd = 'jual'
        usrinput = 'jaul'
        self.assertTrue(match(usrinput, cmd))

    def test_more_char(self):
        cmd = 'panen'
        usrinput = 'paanen'
        self.assertTrue(match(usrinput, cmd))

    def test_more_chars(self):
        cmd = 'lihat'
        usrinput = 'liihaatt'
        self.assertFalse(match(usrinput, cmd))

    def test_with_defined_limit(self):
        cmd = 'kirim'
        usrinput = 'kirimmm'
        self.assertTrue(match(usrinput, cmd, limit=5))

    def test_with_less_char(self):
        cmd = 'tanam'
        usrinput = 'tnam'
        self.assertTrue(match(usrinput, cmd))

    def test_should_not_collide_other_commands(self):
        cmds = [
            'tanam', 'jual', 'panen', 'lihat', 'kirim',
            'plant', 'sell', 'harvest', 'look', 'broadcast'
        ]
        for a in cmds:
            for b in cmds:
                if a != b:
                    self.assertFalse(match(a, b), '{} should not match {}'.format(a, b))

if __name__ == '__main__':
    unittest.main()
