from flask import Flask, request, abort
from app.model.district import District
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param,
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/districts', methods=['POST'])
@ensure_param('name')
@jsonify
def insert():
    name = request.form.get('name')

    existing = District.query(District.name == name).fetch()
    if existing:
        abort(400, 'district {} is already registered'.format(name))

    new = District(id=District.id(), name=name)
    new.put()
    return new.toJson()


@app.route('/v1/districts', methods=['GET'])
@jsonify
def fetch():
    name = request.args.get('name')

    query = District.query()
    if name:
        query = District.query(District.name == name)

    districts = query.order(-District.ts_created).fetch()

    return {
        'districts': [d.toJson() for d in districts]
    }


@app.route('/v1/districts/<district_id>', methods=['GET'])
@jsonify
def retrieve(district_id):
    district = District.get_by_id(district_id)
    if not district:
        abort(404, 'this resource does not exist')

    return district.toJson()
