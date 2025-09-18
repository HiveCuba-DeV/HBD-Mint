import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from .hcdef import CURVE
# ====================================
# 1. Generar par de claves desde private_key_int
# ====================================


def generate_key_pair(private_key_int: int):
    private_key = ec.derive_private_key(private_key_int, CURVE)
    public_key = private_key.public_key()
    return private_key, public_key


# ====================================
# 2. Función de cifrado con la clave pública
# ====================================
def encrypt_message(public_key: EllipticCurvePublicKey, plaintext: bytes) -> str:
    # Clave efímera del emisor
    ephemeral_private = ec.generate_private_key(CURVE)
    ephemeral_public = ephemeral_private.public_key()

    # Secreto compartido ECDH
    shared_secret = ephemeral_private.exchange(ec.ECDH(), public_key)

    # Derivar clave simétrica AES-256
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ecdh-encryption"
    ).derive(shared_secret)

    # AES-GCM
    iv = os.urandom(12)
    encryptor = Cipher(
        algorithms.AES(derived_key), modes.GCM(iv), backend=default_backend()
    ).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Serializar clave pública efímera en formato comprimido
    eph_pub_bytes = ephemeral_public.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    )

    # Construir diccionario JSON seguro (Base64 para binarios)
    enc_dict = {
        "ephemeral_public": base64.b64encode(eph_pub_bytes).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(encryptor.tag).decode(),
    }

    return base64.b64encode(json.dumps(enc_dict)).decode()


# ====================================
# 3. Función de descifrado con la clave privada
# ====================================
def decrypt_message(private_key, enc_json: str) -> bytes:
    # Cargar JSON
    enc_dict = json.loads(base64.b64decode(enc_json).decode())

    # Decodificar base64
    eph_pub_bytes = base64.b64decode(enc_dict["ephemeral_public"])
    iv = base64.b64decode(enc_dict["iv"])
    ciphertext = base64.b64decode(enc_dict["ciphertext"])
    tag = base64.b64decode(enc_dict["tag"])

    # Reconstruir clave pública efímera
    ephemeral_public = ec.EllipticCurvePublicKey.from_encoded_point(
        CURVE, eph_pub_bytes)

    # Derivar secreto compartido
    shared_secret = private_key.exchange(ec.ECDH(), ephemeral_public)

    # Derivar clave simétrica
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ecdh-encryption"
    ).derive(shared_secret)

    # Descifrado AES-GCM
    decryptor = Cipher(
        algorithms.AES(derived_key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext


# ====================================
# DEMO
# ====================================
if __name__ == "__main__":
    private_key_int = 123456789987654321123456789  # Ejemplo

    priv, pub = generate_key_pair(private_key_int)

    msg = b"Mensaje secreto con ECC serializado en JSON!"

    enc_json = encrypt_message(pub, msg)
    print("JSON cifrado:\n", enc_json)

    dec = decrypt_message(priv, enc_json)
    print("\nMensaje descifrado:", dec)
