from flask import Flask, request, abort
from app.model.user import User
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param,
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/users', methods=['POST'])
@ensure_param('phone_number')
@ensure_param('first_name')
@ensure_param('role', enums=User.ROLES)
@jsonify
def insert():
    new = User(id=User.id(),
               role=request.form.get('role'),
               phone_number=request.form.get('phone_number'),
               first_name=request.form.get('first_name'),
               last_name=request.form.get('last_name', None))

    new.put()
    return new.toJson()


@app.route('/v1/users', methods=['GET'])
@jsonify
def fetch():
    phone_number = request.args.get('phone_number')

    query = User.query()
    if phone_number:
        query = User.query(User.phone_number == phone_number)

    users = query.order(-User.ts_created).fetch()

    return {
        'users': [u.toJson() for u in users] if users else []
    }


@app.route('/v1/users/<user_id>', methods=['GET'])
@jsonify
def retrieve(user_id):
    user = User.get_by_id(user_id)
    if not user:
        abort(404, 'this resource does not exist')

    return user.toJson()
