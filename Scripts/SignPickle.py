import base64
import logging

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file = open('Resources/model.pickle', 'rb')
bytes = file.read()

def export_private_key(private_key, filename):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

def export_public_key(public_key, filename):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

def export_signature(signature, filename):
    signature = base64.urlsafe_b64encode(signature)
    with open(filename, 'wb') as f:
            f.write(signature)
   
def sign_model(bytes):
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        signature = private_key.sign(
            data=bytes,
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )

        export_private_key(private_key,'Resources/privkey.pem')
        export_public_key(public_key,'Resources/pubkey.pem')
        export_signature(signature, 'Resources/signature.sig')

        logger.info("Signature: %s", base64.urlsafe_b64encode(signature))

    except UnsupportedAlgorithm:
        logger.exception("Signing failed")

if __name__ == '__main__':
    sign_model(bytes)