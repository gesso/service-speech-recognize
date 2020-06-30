import hashlib
import os
 

def compute_digest(input_fn):
    sha256_hash = hashlib.sha256()
    with open(input_fn, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def get_output_dir(input_fn, digest=None):
    input_digest = compute_digest(input_fn)
    output_dir = os.path.join('output', input_digest)
    return output_dir

