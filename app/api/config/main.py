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

    config = Config.query().fetch()[0]
    admin_username = config.admin_username
    admin_apikey = config.admin_apikey

    if update == 'true':
        admin_username = request.args.get('admin_username')
        admin_apikey = request.args.get('admin_apikey')

        if not admin_username or not admin_apikey:
            abort(400, 'missing required parameters')

        update = config.key.get()
        update.admin_username = admin_username
        update.admin_apikey = admin_apikey
        update.put()

    return {
        'admin_username': admin_username,
        'admin_apikey': admin_apikey
    }
