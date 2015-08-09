from flask import Flask, request, abort
from app.model.config import Config
from app.util.flask_common import (
    jsonify,
    enable_json_error
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/config', methods=['GET'])
@jsonify
def config():
    update = request.args.get('update')

    config = Config()
    existing_configs = Config.query().fetch()
    if existing_configs:
        config = existing_configs[0]

    if update == 'true':
        admin_username = request.args.get('admin_username')
        admin_apikey = request.args.get('admin_apikey')

        if not admin_username or not admin_apikey:
            abort(400, 'missing required parameters')

        config.admin_username = admin_username
        config.admin_apikey = admin_apikey
        config.put()

    return config.toJson()
