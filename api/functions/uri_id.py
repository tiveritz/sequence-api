from hashlib import sha256
from random import randint


def generate_uri_id():
    seed = seed = str.encode(str(randint(0, 10000)))
    hash = sha256(seed)
    start_index = randint(0,57)
    return hash.hexdigest()[start_index:start_index+8]
