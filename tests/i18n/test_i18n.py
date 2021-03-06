import unittest
from app.i18n import _


class i18test(unittest.TestCase):

    def test_command_translate(self):
        self.assertEqual(_('harvest {} {}'), 'panen {} {}')
        self.assertEqual(_('plant {} {}'), 'tanam {} {}')
        self.assertEqual(_('sell {} {}'), 'jual {} {}')
        self.assertEqual(_('look {}'), 'lihat {}')
        self.assertEqual(_('look {} {}'), 'lihat {} {}')
        self.assertEqual(_('broadcast {} {}'), 'kirim {} {}')

    def test_command_param_translate(self):
        self.assertEqual(_('price'), 'harga')
        self.assertEqual(_('all'), 'semua')

    def test_with_domain(self):
        _.domain('idn')

        self.assertEqual(_('potato'), 'kentang')
        self.assertEqual(_('rice'), 'padi')
        self.assertEqual(_('milkfish'), 'bandeng')
        self.assertEqual(_('banana'), 'pisang')

    def test_with_undefined_phrase(self):
        self.assertEqual(_('tokyo'), 'tokyo')
        self.assertEqual(_('london'), 'london')
        self.assertEqual(_('bandung'), 'bandung')

    def test_with_undefined_domain(self):
        _.domain('jp')

        self.assertEqual(_('potato'), 'potato')
        self.assertEqual(_('rice'), 'rice')
        self.assertEqual(_('milkfish'), 'milkfish')
        self.assertEqual(_('banana'), 'banana')
