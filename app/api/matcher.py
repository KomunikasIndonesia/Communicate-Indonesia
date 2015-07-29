import editdistance as ed

LIMIT = 5


def match(usrinput, target):
    dist = ed.eval(usrinput, target)

    return True if dist <= LIMIT else False
