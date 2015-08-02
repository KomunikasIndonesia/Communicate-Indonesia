class i18n(object):

    def __init__(self):
        # Supported languages
        self.lang = ['idn']

        # Default domain
        self._domain = 'idn'

    def domain(self, country):
        if country in self.lang:
            self._domain = country

    def translate(self, domain):
        dic = {}

        dic['idn'] = {
            # Basic commands
            'harvest {} {}':    'panen {} {}',
            'plant {} {}':      'tanam {} {}',
            'sell {} {}':       'jual {} {}',
            'look {}':          'lihat {}',
            'look {} {}':       'lihat {} {}',
            'broadcast {} {}':  'kirim {} {}',
            # Command parameters
            'price':            'harga',
            'all':              'semua',
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
            'clam':             'kerang'
        }
        return dic[domain]

    def __call__(self, string):
        t = self.translate(self._domain)

        if string in t.keys():
            return t[string]
        return string
