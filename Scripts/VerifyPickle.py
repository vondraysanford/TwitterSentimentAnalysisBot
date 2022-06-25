import base64
import logging

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file = open('Resources/model.pickle', 'rb')
bytes = file.read()

def import_private_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None, default_backend())
    return private_key

def import_public_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    public_key = serialization.load_pem_public_key(pemlines, default_backend())
    return public_key

def import_signature(filename):
    with open(filename, 'rb') as sig_in:
        sig_lines = sig_in.read()
    signature = base64.urlsafe_b64decode(sig_lines)
    return signature

def verify_model(bytes):
    try:
        public_key = import_public_key('Resources/pubkey.pem')
        signature = import_signature('Resources/signature.sig')

        public_key.verify(
            signature=signature,
            data=bytes,
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        is_signature_correct = True
    except InvalidSignature:
        is_signature_correct = False

    logger.info("Signature is correct: %s", is_signature_correct)

if __name__ == '__main__':
    verify_model(bytes)