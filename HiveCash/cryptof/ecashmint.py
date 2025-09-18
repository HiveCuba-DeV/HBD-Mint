from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import json

# from hiveManager.hiveuri import genb64U, recb64U
from HiveCash.hiveManager.hiveDrive import existHiveAcount, transferHBD, averifytransactE, aVerifyTransMemo
from HiveCash.tools.checkhex import checkhex
from HiveCash.tools.hashstr import getUMsgHash
from HiveCash.hiveManager.reqDeposit import regDeposit
from ..tools.codeTrans import b64spToHex

from .hcdef import CURVE, SCRYPT_PARAMS, salt, getScryptHash

from beemgraphenebase.account import PrivateKey

from HiveCash.db.dbop import getToken, isMinted, newToken, hdbmint_columnsnames, updateToken

from .acipher import decrypt_message, generate_key_pair

mint_public_hex = {}


def wif_to_keys(wif_active):
    try:
        # Convertir WIF a clave privada usando beem
        private_key_beem = PrivateKey(wif_active)

        # Extraer el entero de la clave privada
        private_key_int = int(private_key_beem.get_secret().hex(), 16)

        return generate_key_pair(private_key_int)

    except Exception as e:
        raise ValueError(f"Error en conversión WIF: {str(e)}") from e
# OK


class EcashMint:
    def __init__(self, wifactive):
        self.private_key, self.public_key = wif_to_keys(wifactive)
        compressed_hex = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        ).hex()
        self.compressed_hex = compressed_hex
        mint_public_hex.update({'hex': compressed_hex})
        print(f'Mint System public key: {compressed_hex}')
    # OK

    def _derive(self, secret: bytes):
        return getScryptHash(secret.hex())
    # OK

    def _sign(self, secret_hash: bytes):
        signature = self.private_key.sign(
            secret_hash,
            ec.ECDSA(hashes.SHA3_256())
        )
        return signature.hex()
    # OK

    def mint_validate(self, secret: bytes, secret_hash: bytes, signature: bytes):
        if secret_hash.hex() == self._derive(secret):
            try:
                self.public_key.verify(
                    signature,
                    secret_hash,
                    ec.ECDSA(hashes.SHA3_256()))
                return True
            except:
                return False
        return False
    # OK

    async def mint_tokens(self, secret_hash: bytes, amount: int):
        if amount < 0:
            raise ValueError("Bad Amount, must be non negative")

        if await isMinted(secret_hash.hex()):
            raise ValueError("Already Minted")

        signature = self._sign(secret_hash)
        uri, memo = regDeposit(secret_hash.hex(), amount)
        return signature, uri, memo
    # Ok

    async def mint_get_sign(self, secret_hash: bytes):
        try:
            tdata = await getToken(secret_hash.hex())
            if len(hdbmint_columnsnames) != len(tdata[0]):
                raise ValueError("Not exist")
            dicdata = dict(zip(hdbmint_columnsnames, tdata[0]))
            amount = int(dicdata.get("amount"))
            status = dicdata.get("status")
            mssg = "Ok"
        except:
            amount = 0
            status = "unmint"
            mssg = "error"

        return self._sign(secret_hash), amount, status, mssg
    # OK

    async def mint_check_deposit(self, secret_hash: bytes):
        tdata = await getToken(secret_hash.hex())
        memo = getUMsgHash(secret_hash.hex())
        if not tdata:  # For unmint
            amount = aVerifyTransMemo(memo)
            if amount != 0:
                try:
                    if not await newToken(secret_hash.hex(), amount):
                        raise ValueError("BD Fail")
                    await updateToken(secret_hash.hex(), {"status": "payed"})
                except:
                    return False
                return True
            return False
        if len(hdbmint_columnsnames) != len(tdata[0]):
            return False
        dicdata = dict(zip(hdbmint_columnsnames, tdata[0]))
        # Only one to onchain
        if dicdata.get('status', "") in ['payed', 'used']:
            return True

        amount = int(dicdata.get("amount"))
        sta = await averifytransactE(amount, memo)
        if sta and dicdata.get("status", "") == 'new':
            await updateToken(secret_hash.hex(), {"status": "payed"})
        return sta
    # OK

    def mint_get_public_key_hex(self):
        return self.compressed_hex
    # OK

    async def mint_internal_transfer(self, tx: str, newhash: str):
        try:
            txu = decrypt_message(self.private_key, tx)
            jsData = json.loads(txu)

            # Get list of tokens
            tokenlist = jsData.get('in', [])
            sversion = jsData.get('version', 0)
            outamount = int(jsData.get('payamount', 0))

            if not newhash:
                return False, "Bad Input: Not output token setted"

            if newhash != bytes.fromhex(newhash).hex():
                return False, "Bad Input: Bad output token format "

            if await isMinted(newhash):
                return False, "Bad Input: Token hash already minted "

            await newToken(newhash, outamount)  # Mint First and wait for funds

            if not tokenlist:
                return False, "Bad Input: Incorrect Data"

            change = jsData.get('ch', [])

            if outamount < 1:
                return False, "Bad Input: Amount to pay"

            # version = int(jsData.get('version', 0))

            inAmount = 0

            # Verifi each token status and acumulative amount
            hashlist = []
            for token in tokenlist:
                if len(token) != 1:  # 3:
                    return False, "Bad Input: incorrect token data size"

                insec = token[0] if sversion == 0 else b64spToHex(token[0])

                if not insec == bytes.fromhex(insec).hex():
                    return False, "Bad Input: incorrect token data"

                ins = getScryptHash(insec)
                hashlist.append(ins)
                tdata = await getToken(ins)
                if len(hdbmint_columnsnames) != len(tdata[0]):
                    return False, "Bad Input: Some token not exist"
                dicdata = dict(zip(hdbmint_columnsnames, tdata[0]))
                amount = int(dicdata.get("amount", 0))
                status = str(dicdata.get("status", ""))

                if amount <= 0:
                    return False, "Bad Input: Incorrect token amount"

                if status == "new":
                    return False, "Bad Input: token not founded"

                if status == "used":
                    return False, "Bad Input: token already used"

                inAmount += amount

            if outamount > inAmount:
                return False, "Bad Input: Not enouch fund to pay"

            if outamount <= inAmount:
                if not change:
                    return False, "Bad Input: Not change defined"
                if len(change) != 1:
                    return False, "Bad Input: Not correct change format"
                changetoken = change[0] if sversion == 0 else b64spToHex(
                    change[0])
                if not changetoken:
                    return False, "Bad Input: Not change token setted"
                if changetoken != bytes.fromhex(changetoken).hex():
                    return False, "Bad Input: Bad change token format "
                if await isMinted(changetoken):
                    return False, "Bad Input: Change Token already minted"

            # Ok set tokens to used and mint
            for hashes in hashlist:
                await updateToken(hashes, {"status": "used"})

            await updateToken(newhash, {"status": "payed"})

            if outamount <= inAmount:
                changetoken = change[0] if sversion == 0 else b64spToHex(
                    change[0])
                await newToken(changetoken, inAmount-outamount)
                if outamount < inAmount:
                    await updateToken(changetoken, {"status": "payed"})
                else:
                    await updateToken(changetoken, {"status": "used"})
            return True, "OK"

        except:
            return False, "TX Error"
        # OK

    async def mint_external_transfer(self, tx: str):
        try:
            txu = decrypt_message(self.private_key, tx)
            jsData = json.loads(txu)

            # Get Data
            tokenlist = jsData.get('in', [])
            if not tokenlist:
                return False, "Bad Input: Incorrect Data"

            change = jsData.get('ch', [])
            if not change:
                return False, "Bad Input: Not change setted"

            out = jsData.get("out", [])
            if not out:
                return False, "Not Output set"

            sversion = jsData.get('version', 0)

            inAmount = 0
            hashlist = []

            # Verify each token status and acumulative amount
            for token in tokenlist:
                if len(token) != 1:
                    return False, "Bad Input: incorrect token data"
                if not checkhex(token):
                    return False, "Bad Input: incorrect token data"

                insec = token[0] if sversion == 0 else b64spToHex(token[0])

                ins = getScryptHash(insec)
                hashlist.append(ins)
                tdata = await getToken(ins)
                if len(hdbmint_columnsnames) != len(tdata[0]):
                    return False, "Bad Input: Some token not exist"
                dicdata = dict(zip(hdbmint_columnsnames, tdata[0]))
                amount = int(dicdata.get("amount", 0))
                status = str(dicdata.get("status", ""))
                if amount <= 0:
                    return False, "Bad Input: Incorrect token amount"
                if status == "new":
                    return False, "Bad Input: token not founded"
                if status == "used":
                    return False, "Bad Input: token already used"

                inAmount += amount

            if len(out) != 3:
                return False, "Bad Input: Not correct output data"

            username = str(out[0])
            if not username:
                return False, "Bad Input: Not output address setted"
            if not await existHiveAcount(username):
                return False, "Bad Input: Output Hive User not exist"

            outamout = int(out[1])
            if outamout < 1:
                return False, "Bad Input: Bad Amount to pay"
            if outamout > inAmount:
                return False, "Bad Input: Not enouch fund to pay"

            memo = str(out[2])

            if outamout <= inAmount:
                changetoken = change[0] if sversion == 0 else b64spToHex(
                    change[0])
                if not changetoken:
                    return False, "Bad Input: Not change token setted"
                if changetoken != bytes.fromhex(changetoken).hex():
                    return False, "Bad Input: Bad change token format "
                if await isMinted(changetoken):
                    return False, "Bad Input: Change Token already minted"

           # Send to external wallet here
            if not await transferHBD(username, outamout, memo):
                return False, "TX Error: Connection RPC fail "

            # Ok set tokens to used
            for hashes in hashlist:
                await updateToken(hashes, {"status": "used"})

            if outamout <= inAmount:
                changetoken = change[0] if sversion == 0 else b64spToHex(
                    change[0])
                await newToken(changetoken, inAmount-outamout)
                if outamout < inAmount:
                    await updateToken(changetoken, {"status": "payed"})
                else:
                    await updateToken(changetoken, {"status": "used"})

            return True, "OK"

        except:
            return False, "TX Error"
    # OK
