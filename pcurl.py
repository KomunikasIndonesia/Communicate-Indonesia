import argparse
import json
import os
import requests


ENV_URL = {
    'local': 'http://localhost:8080',
    'stage': 'https://communicate-indonesia-staging.appspot.com'
}


class API(object):

    def __init__(self, url, config):
        self.url = url
        self.config = config
        self.auth = (config['admin_username'], config['admin_apikey'])

    def _get_data(self, params):
        data = {}

        for param, default in params.items():
            if default:
                value = raw_input('---- "{}" ? ({})\n'.format(param, default)) or default
            else:
                value = raw_input('---- "{}" ?\n'.format(param))

            if value:
                data[param] = value

        return data

    def list(self, params=None):
        return requests.get(self.url,
                            params=self._get_data(params),
                            auth=self.auth).content

    def get(self):
        data = self._get_data({'id': None})
        return requests.get(self.url + '/{}'.format(data['id']),
                            auth=self.auth).content

    def create(self, params=None):
        return requests.post(self.url,
                             data=self._get_data(params),
                             auth=self.auth).content


class UserAPI(API):

    def __init__(self, base_url, config):
        super(UserAPI, self).__init__(base_url + '/v1/users', config)

    def list(self):
        return super(UserAPI, self).list({'phone_number': None})

    def create(self):
        return super(UserAPI, self).create({
            'first_name': None,
            'last_name': None,
            'phone_number': None,
            'district_id': None,
            'role': None
        })


class DistrictAPI(API):

    def __init__(self, base_url, config):
        super(DistrictAPI, self).__init__(base_url + '/v1/districts', config)

    def list(self):
        return super(DistrictAPI, self).list({'name': None})

    def create(self):
        return super(DistrictAPI, self).create({'name': None})


def configure():
    print('-' * 80)
    print('pcurl config is not set')
    print('modify .pcurl.config')
    print('-' * 80)
    with open('.pcurl.config', 'w') as f:
        f.write(json.dumps({
            'prod': {
                'admin_username': '-',
                'admin_apikey': '-'
            },
            'stage': {
                'admin_username': '-',
                'admin_apikey': '-'
            },
            'local': {
                'admin_username': '-',
                'admin_apikey': '-'
            }
        }, indent=4, sort_keys=True))


def main():
    if not os.path.isfile('.pcurl.config'):
        configure()
        exit()

    config = None
    with open('.pcurl.config', 'r') as f:
        config = json.loads(f.read())

    parser = argparse.ArgumentParser(description='curl wrapper around the '
                                                 'api for common operations')
    parser.add_argument('env',
                        choices=['local', 'stage', 'prod'],
                        default='local',
                        help='the deployed environment')
    parser.add_argument('api',
                        choices=['users', 'districts'],
                        help='the api endpoint')
    parser.add_argument('operation',
                        choices=['list', 'create', 'get'],
                        help='[the operation to perform')

    args = parser.parse_args()

    config = config[args.env]
    base_url = ENV_URL[args.env]
    api_map = {
        'users': UserAPI(base_url, config),
        'districts': DistrictAPI(base_url, config)
    }

    content = getattr(api_map[args.api], args.operation)()

    print('-' * 80)
    print(content)
    print('-' * 80)


if __name__ == '__main__':
    main()
