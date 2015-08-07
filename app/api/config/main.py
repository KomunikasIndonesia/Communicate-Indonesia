from flask import Flask, request, abort
from app.model.config import Config, delete_config
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    require_apikey
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/config', methods=['GET'])
@require_apikey
@jsonify
def config():
    update = request.args.get('update')

    if update == 'true':
        admin_username = request.args.get('admin_username')
        admin_apikey = request.args.get('admin_apikey')

        if not admin_username or not admin_apikey:
            abort(400, 'missing required parameters')

        new = Config(admin_username=admin_username,
                     admin_apikey=admin_apikey)
        delete_config()
        new.put()

    else:
        config = Config.query().fetch()[0]
        admin_username = config.admin_username
        admin_apikey = config.admin_apikey

    return {
        'admin_username': admin_username,
        'admin_apikey': admin_apikey
    }
