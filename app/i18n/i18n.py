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
            'register':         'mendaftar',
            'harvest {} {}':    'panen {} {}',
            'plant {} {}':      'tanam {} {}',
            'sell {} {}':       'jual {} {}',
            'look {}':          'lihat {}',
            'look {} {}':       'lihat {} {}',
            'broadcast {} {}':  'kirim {} {}',
            # Command parameters
            'price':            'harga',
            'all':              'semua',
            'everyone':         'semua',
            # Command output
            'Plant already registered':     'Tanaman sudah terdaftar',
            'Register command succeded':    'Daftar perintah berhasil',
            'Plant command succeeded':      'Perintah tanam berhasil',
            'Not enough {} planted':        'Tanam belum mencukupi',
            'Harvest command succeeded':    'Perintah panen berhasil',
            'Not enough {} harvested':      'Panen belum mencukupi',
            'Sell command succeeded':       'Perintah jual berhasil',
            'Unknown command':              'Perintah tidak dikenal',

            'Unknown command, valid format below:\n'
            'PLANT [qty] [type]\n'
            'HARVEST [qty] [type]\n'
            'SELL [qty] [type]\n'
            'REGISTER [plant] [weight|volume|count]\n'
            'BROADCAST [msg]':              'Perintah tidak dikenal, ketik cara berikut:\n'
                                            'TANAM [jumlah] [jenis]\n'
                                            'PANEN [jumlah] [jenis]\n'
                                            'JUAL [jumlah] [jenis]\n'
                                            'Mendaftar [tanaman] [berat|volume|biji]',

            'Message delivered':            'Pesan berhasil dikirim',
            'Message delivery failed':      'Pesan gagal dikirim',

            'Plant not registered':         'Tanaman belum terdaftar',
            'Invalid unit for {} command':  'Unit tidak diketahui',
            # Query district
            'Total {} in {}:':              'Total {} di {}:',
            '{} data is none':              'Data {} tidak ada',
            'Command not allowed':          'Perintah tidak diizinkan',
            'District {} is unknown':       'Daerah {} tidak diketahui',
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
            'mango':            'mangga',
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
            'December':         'Desember',

            # Units
            'weight':           'berat',
            'volume':           'volume',
            'farm item':        'biji',
        }

        return dic[domain] if domain in dic else {}

    def __call__(self, string):
        t = self.translate(self._domain)

        if string in t.keys():
            return t[string]
        return string
