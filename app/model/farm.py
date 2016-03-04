import time
from .util import id
from google.appengine.ext import ndb


class UnitConverter(object):
    UNITS = [
        (1, '')
    ]
    _reverse_index = {unit: multiplier for multiplier, unit in UNITS}

    @classmethod
    def largest_unit(cls, quantity, unit):
        original_multiplier = cls._reverse_index[unit]
        quantity = quantity * original_multiplier

        for multiplier, possible_unit in reversed(cls.UNITS):
            if quantity / multiplier >= 1:
                return possible_unit

        # fallback to smallest unit
        return cls.UNITS[0][1]

    @classmethod
    def convert_to_unit(cls, quantity, original_unit, to_unit):
        original_multiplier = cls._reverse_index[original_unit]
        to_multiplier = cls._reverse_index[to_unit]
        return quantity * original_multiplier / to_multiplier


class WeightConverter(UnitConverter):
    UNITS = [
        (1, 'g'),
        (1000, 'kg')
    ]
    _reverse_index = {unit: multiplier for multiplier, unit in UNITS}


class VolumeConverter(UnitConverter):
    UNITS = [
        (1, 'L'),
        (1000, 'kL')
    ]
    _reverse_index = {unit: multiplier for multiplier, unit in UNITS}


class Farm(ndb.Model):
    ACTION = ['harvest', 'plant', 'sell']
    DEFAULT_UNITS = {
        'weight': ('g', WeightConverter),
        'volume': ('L', VolumeConverter),
        'count': ('', UnitConverter)
    }

    # relationship
    district_id = ndb.StringProperty(required=True)

    # farm properties
    action = ndb.StringProperty(required=True, choices=set(ACTION))
    crop_name = ndb.StringProperty(required=True)
    quantity = ndb.IntegerProperty(required=True)
    unit_type = ndb.StringProperty(required=True, choices=DEFAULT_UNITS.keys())
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def toJson(self):
        return {
            'id': self.key.id(),
            'district_id': self.district_id,
            'action': self.action,
            'crop_name': self.crop_name,
            'quantity': self.quantity,
            'unit_type': self.unit_type,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @property
    def quantity_and_unit(self):
        unit, converter = self.DEFAULT_UNITS[self.unit_type]

        largest_unit = converter.largest_unit(self.quantity, unit)
        quantity = converter.convert_to_unit(self.quantity, unit, largest_unit)

        return '{} {}'.format(quantity, largest_unit).strip()

    @staticmethod
    def id():
        return 'F{}'.format(id.generate())
