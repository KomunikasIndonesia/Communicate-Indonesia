from flask import Flask, request, abort
from app.model.district import District
from app.model.user import User
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param,
    require_apikey
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/users', methods=['POST'])
@require_apikey
@ensure_param('phone_number')
@ensure_param('first_name')
@ensure_param('role', enums=User.ROLES)
@jsonify
def insert():
    role = request.form.get('role')
    district_id = request.form.get('district_id', None)

    if role == User.ROLE_FARMER or role == User.ROLE_DISTRICT_LEADER:
        if not district_id:
            abort(400, 'district_id is required')

        district = District.get_by_id(district_id)
        if not district:
            abort(400, '{} is an invalid district_id'.format(district_id))

    new = User(id=User.id(),
               role=role,
               district_id=district_id,
               phone_number=request.form.get('phone_number'),
               first_name=request.form.get('first_name'),
               last_name=request.form.get('last_name', None))

    new.put()
    return new.to_dict()


@app.route('/v1/users', methods=['GET'])
@require_apikey
@jsonify
def fetch():
    phone_number = request.args.get('phone_number')

    query = User.query()
    if phone_number:
        query = User.query(User.phone_number == phone_number)

    users = query.order(-User.ts_created).fetch()

    return {
        'users': [u.to_dict() for u in users] if users else []
    }


@app.route('/v1/users/<user_id>', methods=['GET'])
@require_apikey
@jsonify
def retrieve(user_id):
    user = User.get_by_id(user_id)
    if not user:
        abort(404, 'this resource does not exist')

    return user.to_dict()
