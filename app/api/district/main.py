from flask import Flask, request, abort
from app.model.district import District
from app.util.flask_common import (
    jsonify,
    enable_json_error,
    ensure_param,
    require_apikey
)


app = Flask(__name__)
enable_json_error(app)


@app.route('/v1/districts', methods=['POST'])
@require_apikey
@ensure_param('name')
@jsonify
def insert():
    name = request.form.get('name')
    slug = name.lower()

    existing = District.query(District.slug == slug).fetch()
    if existing:
        abort(400, 'district {} is already registered'.format(name))

    new = District(id=District.id(), name=name, slug=slug)
    new.put()
    return new.to_dict()


@app.route('/v1/districts', methods=['GET'])
@require_apikey
@jsonify
def fetch():
    name = request.args.get('name')

    query = District.query()
    if name:
        query = District.query(District.slug == name.lower())

    districts = query.order(-District.ts_created).fetch()

    return {
        'districts': [d.to_dict() for d in districts]
    }


@app.route('/v1/districts/<district_id>', methods=['GET'])
@require_apikey
@jsonify
def retrieve(district_id):
    district = District.get_by_id(district_id)
    if not district:
        abort(404, 'this resource does not exist')

    return district.to_dict()
