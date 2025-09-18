from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.asymmetric import ec

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin
from hdwallet.seeds import BIP39Seed
from hdwallet.derivations import BIP44Derivation
from mnemonic import Mnemonic

import os

CURVE = ec.SECP256K1()

SCRYPT_PARAMS = {
    "length": 32,
    "n": 16384,
    "r": 8,
    "p": 1
}

salt = b'HiveCash'


def getScryptHash(msg: str):
    return Scrypt(salt=salt, **
                  SCRYPT_PARAMS).derive(bytes(msg, encoding='utf-8')).hex()


MNEMONIC = os.environ.get("MNEMONIC")


lastid = 0

if not MNEMONIC:
    raise ValueError(
        "Debe definir la clave privada mnemonica de 12  palabras!!!")

mnemo = Mnemonic("english")

seed = mnemo.to_seed(MNEMONIC)
bip39_seed = BIP39Seed(seed=seed)


def getHDprivate():
    global lastid
    hdwallet = HDWallet(cryptocurrency=Bitcoin)
    hdwallet.from_seed(seed=bip39_seed)
    # "m/44'/0'/0'/0/{lastid}"
    derivation = BIP44Derivation(
        account=0,
        change=False,
        address=lastid
    )
    hdwallet.from_derivation(derivation=derivation)
    lastid += 1
    return str(hdwallet.private_key())


# for test, comment all for production
#sec0 = getHDprivate()
#hash0 = getScryptHash(sec0)
#print("First Private and hash")
#print(f"Private: {sec0}")
#print(f"Hash: {hash0}")

#sec0 = getHDprivate()
#hash0 = getScryptHash(sec0)
#print("Second Private and hash")
#print(f"Private: {sec0}")
#print(f"Hash: {hash0}")

#sec0 = getHDprivate()
#hash0 = getScryptHash(sec0)
#print("3st Private and hash")
#print(f"Private: {sec0}")
#print(f"Hash: {hash0}")
