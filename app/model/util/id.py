import uuid


def generate():
    return str(uuid.uuid1()).replace('-', '')
