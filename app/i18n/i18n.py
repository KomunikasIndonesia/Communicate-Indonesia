class i18n(object):

    def __init__(self):
        # Default domain
        self._domain = 'idn'

    def domain(self, country):
        self._domain = country

    def translate(self, domain):
        dic = {}

        dic['idn'] = {
            # Basic commands
            'harvest':          'panen',
            'plant':            'tanam',
            'sell':             'jual',
            'harvest {} {}':    'panen {} {}',
            'plant {} {}':      'tanam {} {}',
            'sell {} {}':       'jual {} {}',
            'look {}':          'lihat {}',
            'look {} {}':       'lihat {} {}',
            'broadcast {} {}':  'kirim {} {}',
            # Command parameters
            'price':            'harga',
            'all':              'semua',
            # Command output
            'Plant command succeeded':      'Perintah tanam berhasil',
            'Harvest command succeeded':    'Perintah panen berhasil',
            'Sell command succeeded':       'Perintah jual berhasil',
            'Unknown command':              'Perintah tidak dikenal',
            # Query district
            'Total {} in {}:':              'Total {} di {}:',
            '{} data is none':              'Data {} tidak ada',
            # Vegetable crops
            'rice':             'padi',
            'potato':           'kentang',
            'tomato':           'tomat',
            'corn':             'jagung',
            'cabbage':          'kubis',
            'carrot':           'wortel',
            'onion':            'bawang',
            'redonion':         'bawangmerah',
            'garlic':           'bawangputih',
            'lettuce':          'selada',
            'radish':           'lobak',
            'eggplant':         'terong',
            'cucumbers':        'timun',
            # Fruit crops
            'strawberry':       'stroberi',
            'banana':           'pisang',
            'pineapple':        'nanas',
            # Fish farmers
            'shrimp':           'udang',
            'fish':             'ikan',
            'milkfish':         'bandeng',
            'catfish':          'lele',
            'squid':            'cumicumi',
            'clam':             'kerang',
            # Month
            'January':          'Januari',
            'February':         'Februari',
            'March':            'Maret',
            'April':            'April',
            'May':              'Mei',
            'June':             'Juni',
            'July':             'Juli',
            'August':           'Agustus',
            'September':        'September',
            'October':          'Oktober',
            'November':         'November',
            'December':         'Desember'
        }

        return dic[domain] if domain in dic else {}

    def __call__(self, string):
        t = self.translate(self._domain)

        if string in t.keys():
            return t[string]
        return string
