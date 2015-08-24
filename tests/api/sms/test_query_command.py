import unittest

from app.api.sms.query_action import QueryCommand
from app.model.sms_request import SmsRequest


class QueryCommandTest(unittest.TestCase):

    def test_query_command(self):
        valid_messages = [
            {
                'filter': ['harvest', 'panen'],
                'msg': [
                    'look lompoko harvest',
                    'look harvest lompoko',
                    'look lompoko',  # default harvest
                    'lihat lompoko panen',
                    'lihat panen lompoko',
                    'lihat lompoko'  # default harvest
                ]
            },
            {
                'filter': ['plant', 'tanam'],
                'msg': [
                    'look lompoko plant',
                    'look plant lompoko',
                    'lihat lompoko tanam',
                    'lihat tanam lompoko'
                ]
            },
            {
                'filter': ['sell', 'jual'],
                'msg': [
                    'look lompoko sell',
                    'look sell lompoko',
                    'lihat lompoko jual',
                    'lihat jual lompoko'
                ]
            }
        ]

        for valid in valid_messages:
            for body in valid['msg']:
                sms = SmsRequest()
                sms.body = body

                cmd = QueryCommand(sms)
                self.assertTrue(cmd.valid())
                self.assertTrue(cmd.filter in valid['filter'])
                self.assertEqual('lompoko', cmd.district)

    def test_query_command_without_district(self):
        invalid_messages = [
            'look harvest',
            'look plant',
            'look sell',
            'lihat panen',
            'lihat tanam',
            'lihat jual'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body

            cmd = QueryCommand(sms)
            self.assertFalse(cmd.valid())

    def test_query_command_with_invalid_command(self):
        invalid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body

            cmd = QueryCommand(sms)
            self.assertFalse(cmd.valid())
