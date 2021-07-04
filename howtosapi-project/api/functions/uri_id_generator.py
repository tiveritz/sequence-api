from hashlib import sha256
from random import randint


def generate(seed):
    seed = str.encode(str(seed))
    hash = sha256(seed)

    start_index = randint(0,57)
    return hash.hexdigest()[start_index:start_index+8]
